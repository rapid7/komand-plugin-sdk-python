from flask import Flask, Response, jsonify, request
import logging
import gunicorn.app.base
from gunicorn.six import iteritems
from .exceptions import *
SERVER_INSTANCE = None


class PluginServer(object):
    """
    Server which runs the plugin as an HTTP server.

    From the Komand Proxy:

      // const URLPattern = "<vendor>/<plugin>/<version>/<type>/<name>[/<test>]"
      // EX: komand/slack/1.0.1/actions/post_message/
      // EX: komand/slack/1.0.1/actions/post_message/test
      // EX: komand/slack/1.0.1/triggers/message/test
      // Non tests of triggers are not supported
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
            input_message = request.get_json(force=True)
            logging.info('request json: %s', input_message)
            status_code = 200
            output = None
            try:
                output = self.plugin.handle_step(input_message, is_debug=self.debug, is_test=test is not None)
            except LoggedException as e:
                wrapped_exception = e.ex
                output = e.output

                if isinstance(wrapped_exception, ClientException):
                    status_code = 400
                elif isinstance(wrapped_exception, ServerException):
                    # I'm unsure about this
                    status_code = 500
                else:
                    status_code = 500
            finally:
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
