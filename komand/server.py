from flask import g, Flask, jsonify, request
import logging
import copy
from io import StringIO
import komand.message as message
import komand.action
import komand.dispatcher
import gunicorn.app.base
from gunicorn.six import iteritems


def create_flask_app():
    app = Flask(__name__)

    @app.route('/<string:prefix>/<string:name>', defaults={'test': None}, methods=['POST'])
    @app.route('/<string:prefix>/<string:name>/<string:test>', methods=['POST'])
    def handler(prefix, name, test):
        msg = request.get_json()
        if request.method == 'POST':
            dummy = request.form
        if not g.control:
            logging.fatal("Fatal error - no control server provided")

        is_test = test is not None
        logging.info('request json: %s', msg)
        result = {}
        if prefix == "actions":
            try:
                result = g.control.handle_action(name, msg, is_test)
            except Exception as ex:
                logging.fatal("Exception while running http handler for action: %s", ex)
                response = jsonify(message.ActionError(meta={}))
                response.status_code = 400
                return response
        elif prefix == "triggers" and is_test:
            try:
                result = g.control.handle_trigger(name, msg)
            except Exception as ex:
                logging.fatal("Exception while running http handler for trigger: %s", ex)
                response = jsonify(message.TriggerEvent(meta={}, output={}))
                response.status_code = 400
                return response
        else:
            # It wasn't an action, and it wasn't a trigger test, so it was a trigger non test
            # Not supported, return error
            logging.fatal("Fatal error - must specify either actions or triggers in the url")
            response = jsonify(message.TriggerEvent(meta={}, output={}))
            response.status_code = 400
            return response

        response = jsonify(result)
        if 'plugin_error' in result:
            response.status_code = 500
        return response
    return app


class Server(object):
    """Server runs the plugin in server mode"""
    def __init__(self, plugin, port=10001, debug=False):
        self.plugin = plugin
        self.port = port
        self.debug = debug
        self.app = create_flask_app()

    def start(self):
        """ start server """
        logging.info("Starting server on port %d" % self.port)

        with self.app.app_context():
            g.control = self
            options = {
                'bind': '%s:%s' % ('0.0.0.0', self.port),
                'workers': ApplicationServer.number_of_workers(),
            }
            logging.info("Binding app to control")
            ApplicationServer(self.app, options).run()

    def handle_action(self, name, msg, is_test):
        """Run handler"""
        if name not in self.plugin.actions:
            return message.ActionError({}, ('No action found %s' % name), "")
        meta = {}
        if 'body' in msg and msg['body']['meta']:
            meta = msg['body']['meta']
        act = self.plugin.actions[name]
        act = copy.copy(act)
        act.setupLogger()

        if msg['type'] != message.ACTION_START:
            return message.ActionError(meta, ('Invalid message type %s' % msg['type']), "")

        dispatch = komand.dispatcher.Noop()

        task = komand.action.Task(
            connection=self.plugin.connection_cache.get(msg['body']['connection']),
            action=act,
            msg=msg['body'],
            connection_cache=self.plugin.connection_cache,
            dispatch=dispatch,
            custom_encoder=self.plugin.custom_encoder,
            custom_decoder=self.plugin.custom_decoder)
        if is_test:
            task.test()
        else:
            task.run()
        # dispatch.msg has the envelope and message body with error codes and logs
        return dispatch.msg

    def handle_trigger(self, name, msg):
        """Run handler"""
        if name not in self.plugin.triggers:
            return message.ActionError({}, ('No action found %s' % name), "")
        meta = {}
        if 'body' in msg and msg['body']['meta']:
            meta = msg['body']['meta']
        trig = self.plugin.triggers[name]
        trig = copy.copy(trig)
        trig.setupLogger()

        if msg['type'] != message.TRIGGER_START:
            return message.ActionError(meta, ('Invalid message type %s' % msg['type']), "")

        dispatch = komand.dispatcher.Noop()

        task = komand.trigger.Task(
            connection=self.plugin.connection_cache.get(msg['body']['connection']),
            trigger=trig,
            msg=msg['body'],
            connection_cache=self.plugin.connection_cache,
            dispatch=dispatch,
            custom_encoder=self.plugin.custom_encoder,
            custom_decoder=self.plugin.custom_decoder)
        task.test()
        # dispatch.msg has the envelope and message body with error codes and logs
        return dispatch.msg


class ApplicationServer(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(ApplicationServer, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

    @staticmethod
    def number_of_workers():
        import multiprocessing
        return (multiprocessing.cpu_count() * 2) + 1
