import logging

import gunicorn.app.base
from flask import Flask, jsonify, request, abort
from gunicorn.six import iteritems

from .exceptions import ClientException, ServerException, LoggedException

SERVER_INSTANCE = None


class PluginServer(object):
    """
    Server which runs the plugin as an HTTP server.

    Serves the following endpoints:

    POST http://host/actions/[action]        Executes action's run method
    POST http://host/actions/[action]/test   Executes action's test method
    POST http://host/triggers/[trigger]/test Executes trigger's test method

    NOTE: starting a trigger is not supported. Triggers should be started in legacy mode.

    """

    def __init__(self, plugin, port=10001, debug=False):
        self.plugin = plugin
        self.port = port
        self.debug = debug
        self.app = self.create_flask_app()

    def create_flask_app(self):
        app = Flask(__name__)

        @app.route('/<string:prefix>/<string:name>', defaults={'test': None}, methods=['POST'])
        @app.route('/<string:prefix>/<string:name>/<string:test>', methods=['POST'])
        def handler(prefix, name, test):

            if test is None and prefix == 'triggers':
                # Guard against starting triggers
                return abort(404)

            input_message = request.get_json(force=True)
            logging.info('request input: %s', input_message)
            status_code = 200
            output = None
            try:
                output = self.plugin.handle_step(input_message, is_debug=self.debug, is_test=test is not None)
            except LoggedException as e:
                wrapped_exception = e.ex
                logging.exception(wrapped_exception)
                output = e.output

                if isinstance(wrapped_exception, ClientException):
                    status_code = 400
                elif isinstance(wrapped_exception, ServerException):
                    # I'm unsure about this
                    status_code = 500
                else:
                    status_code = 500
            finally:
                logging.info('request output: %s', output)
                r = jsonify(output)
                r.status_code = status_code
                return r

        return app

    def start(self):
        """ start server """
        with self.app.app_context():
            global SERVER_INSTANCE
            SERVER_INSTANCE = self
            options = {
                'bind': '%s:%s' % ('0.0.0.0', self.port),
                'workers': GunicornServer.number_of_workers(),
                'threads': 4
            }
            GunicornServer(self.app, options).run()


class GunicornServer(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(GunicornServer, self).__init__()

    def init(self, parser, opts, args):
        pass

    def load(self):
        return self.application

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    @staticmethod
    def number_of_workers():
        return 4
