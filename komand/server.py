import sys
import os
import subprocess
import signal

import gunicorn.app.base
from flask import Flask, jsonify, request, abort
from gunicorn.arbiter import Arbiter
from gunicorn.six import iteritems

from .exceptions import ClientException, ServerException, LoggedException


class PluginServer(gunicorn.app.base.BaseApplication):
    """
    Server which runs the plugin as an HTTP server.

    Serves the following endpoints:

    POST http://host/actions/[action]        Executes action's run method
    POST http://host/actions/[action]/test   Executes action's test method
    POST http://host/triggers/[trigger]/test Executes trigger's test method

    NOTE: starting a trigger is not supported. Triggers should be started in legacy mode.

    """

    def __init__(self, plugin, port=10001, workers=1, threads=4, debug=False):
        self.gunicorn_config = {
            'bind': '%s:%s' % ('0.0.0.0', port),
            'workers': workers,
            'threads': threads,
            'loglevel': 'debug' if debug else 'info'
        }
        super(PluginServer, self).__init__()
        self.plugin = plugin
        self.debug = debug
        self.app = self.create_flask_app()
        self.master_pid = os.getpid()

    def init(self, parser, opts, args):
        pass

    def load(self):
        return self.app

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.gunicorn_config)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def create_flask_app(self):
        app = Flask(__name__)

        @app.route('/<string:prefix>/<string:name>', defaults={'test': None}, methods=['POST'])
        @app.route('/<string:prefix>/<string:name>/<string:test>', methods=['POST'])
        def handler(prefix, name, test):

            input_message = request.get_json(force=True)
            self.logger.debug('Request input: %s', input_message)

            if input_message is None:
                return abort(400)

            # Enforce contract where path component MUST be "test"
            if (test is not None) and (test.lower() != "test"):
                return abort(400)

            # Ensure url matches action/trigger name in body
            if prefix == 'actions':
                if input_message.get('body', {}).get('action', None) != name:
                    return abort(400)
            elif prefix == 'triggers':
                if test is None:
                    # Guard against starting triggers
                    return abort(404)
                if input_message.get('body', {}).get('trigger', None) != name:
                    return abort(400)
            else:
                return abort(404)

            status_code = 200
            output = None
            try:
                output = self.plugin.handle_step(input_message, is_debug=self.debug, is_test=test is not None)
            except LoggedException as e:
                wrapped_exception = e.ex
                self.logger.exception(wrapped_exception)
                output = e.output

                if isinstance(wrapped_exception, ClientException):
                    status_code = 400
                elif isinstance(wrapped_exception, ServerException):
                    # I'm unsure about this
                    status_code = 500
                else:
                    status_code = 500
            finally:
                self.logger.debug('Request output: %s', output)
                r = jsonify(output)
                r.status_code = status_code
                return r

        @app.route("/workers/add", methods=["POST"])
        def add_worker():
            """
            Adds a worker (another process)
            :return: Json Response
            """
            r = {}

            # Linux signal examples here:
            # https://docs.gunicorn.org/en/stable/signals.html#master-process
            try:
                self.logger.info("Adding a worker")
                self.logger.info("Current process is: %s" % self.master_pid)
                os.kill(self.master_pid, signal.SIGTTIN)
            except Exception as e:
                r.status_code = 500
                r.error = e
                return jsonify(r)

            r["num_workers"] = self._number_of_workers()
            return jsonify(r)

        @app.route("/workers/remove", methods=["POST"])
        def remove_worker():
            """
            Shuts down a worker (another process)
            If there is only 1 worker, nothing happens

            :return: Json Response
            """

            r = {}

            # Linux signal examples here:
            # https://docs.gunicorn.org/en/stable/signals.html#master-process
            try:
                self.logger.info("Removing a worker")
                self.logger.info("Current process is: %s" % self.master_pid)
                os.kill(self.master_pid, signal.SIGTTOU)
            except Exception as e:
                r = {}
                r.status_code = 500
                r.error = e
                return jsonify(r)

            return jsonify(r)  # Flask or Gunicorn expect a return

        @app.route("/workers", methods=["GET"])
        def num_workers():
            r = {'num_workers': self._number_of_workers()}
            return jsonify(r)

        # Return flask app
        return app

    def _number_of_workers(self):
        """
        Number of workers tries to return the number of workers in use for gunicorn
        It finds all processes named komand or icon and returns the number it finds minus 1.

        The minus 1 is due to gunicorn always having a master process and at least 1 worker.

        This function will likely produce unreliable results if used outside of a docker container

        :return: integer
        """
        output = subprocess.check_output('ps | grep "icon\\|komand" | grep -v "grep" | wc -l', shell=True)
        num_workers = int(output.decode())

        # num_workers - 1 due to a master process being run as well
        return num_workers - 1

    def start(self):
        """ start server """
        with self.app.app_context():
            try:
                arbiter = Arbiter(self)
                self.logger = arbiter.log
                arbiter.run()

            except RuntimeError as e:
                sys.stderr.write("\nError: %s\n" % e)
                sys.stderr.flush()
                sys.exit(1)
