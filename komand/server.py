from flask import g, Flask, jsonify, request
import logging
import copy
from io import StringIO
import komand.message as message
import komand.action
import komand.dispatcher

# this is global...
# there can only be one app in python servers i guess.
# I don't know. :shrug:
# lol python
app = Flask(__name__)

@app.route("/test")
def testy():
    return jsonify({"hey":"hi"})

@app.route('/actions/<string:name>', methods=['PUT', 'POST'])
def action(name):
    logging.error("ACTION IS %s", name)
    if request.method == 'POST':
        dummy = request.form
    if not g.control:
        logging.fatal("Fatal error - no control server provided")

    msg = request.get_json()

    logging.error('request json: %s', msg)

    # TODO: wrap in antoher try/catch and capture any errors
    result = g.control.handle(name, msg)
    response = jsonify(result)
    if 'plugin_error' in result:
        response.status_code = 500

    return response

class Server(object):
    """Server runs the plugin in server mode"""
    def __init__(self, plugin, port=10001, debug=False):
        self.plugin = plugin
        self.port = port
        self.debug = debug

    def start(self):
        """ start server """
        with app.app_context():
            g.control = self
            logging.info("Starting server on port: %d", self.port)
            app.run(host='0.0.0.0', port=self.port)

    def handle(self, name, msg):
        """Run handler"""
        if not name in self.plugin.actions:
            return message.ActionError({}, ('No action found %s' % name), "")

        act = self.plugin.actions[name]
        act = copy.copy(act)
        act.setupLogger()
        logging.error("~~~~~~~~~~")
        logging.error(msg)
        logging.error("~~~~~~~~~~")

        if msg['type'] != message.ACTION_START:
            return message.ActionError(act.meta, ('Invalid message type %s' % msg['type']), "")

        dispatch = komand.dispatcher.Noop()

        task = komand.action.Task(
            connection=None,
            action=act,
            msg=msg['body'],
            connection_cache=self.plugin.connection_cache,
            dispatch=dispatch,
            custom_encoder=self.plugin.custom_encoder,
            custom_decoder=self.plugin.custom_decoder)

        task.run()

        logs = act.logs()
        output = dispatch.msg

        if 'body' in output and output['body']['status'] == message.ERROR:
            return message.ActionError(act.meta, output['body']['error'], logs)
        return message.ActionSuccess(act.meta, output, logs)
