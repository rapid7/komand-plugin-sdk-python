import komand.message as message
import komand.dispatcher as dispatcher
import logging
import inspect


class Trigger(object):
    """A trigger"""
    def __init__(self, name, description, input, output):
        self.name = name 
        self.description = description 
        self.connection = None
        self._sender = None
        self.input = input
        self.output = output
        self.webhook_url = ''

    def send(self, event):
        schema = self.output
        if schema:
            schema.validate(event)

        self._sender.send(event)

    def run(self, params={}):
        """ Run a trigger. Returns nothing """
        raise NotImplementedError

    def test(self, params={}):
        """ Test a trigger.  Should return output JSON """
        raise NotImplementedError


class Task(object):
    """Task to run or test an trigger"""
    def __init__(self, connection, trigger, msg, dispatch=None, custom_encoder=None, custom_decoder=None):
        self.connection = connection
        self.trigger = trigger
        self.msg = msg
        self.dispatcher = dispatch
        self.custom_encoder = custom_encoder
        self.custom_decoder = custom_decoder
        self.meta = None
        self.debug = False

    def send(self, output):
        msg = message.trigger_event(meta=self.meta, output=output)
        self.dispatcher.write(msg)

    def test(self):
        """ Run test """
        dparams = self.msg.get('dispatcher', {})
        dparams["custom_encoder"] = self.custom_encoder
        dparams["custom_decover"] = self.custom_decoder
        dispatch = dispatcher.Stdout(dparams)

        try:
            self._setup(False)
            params = {}
            if self.trigger and self.trigger.input.parameters:
                params = self.trigger.input.parameters

            args = inspect.getargspec(self.trigger.test).args

            if len(args) == 1:
                output = self.trigger.test()
            else:
                output = self.trigger.test(params)

        except Exception as e:
            logging.exception('trigger test failure: %s', e)
            return False

        msg = message.trigger_event(meta=self.meta, output=output)
        dispatch.write(msg)
        return True

    def run(self):
        """ Run the trigger"""
        try:
            self._setup()
            self.trigger._sender = self
            params = {}
            if self.trigger and self.trigger.input.parameters:
                params = self.trigger.input.parameters

            self.trigger.run(params)
        except Exception as e:
            logging.exception('trigger test failure: %s', e)
            # XXX: exit code??
            return

    def _setup(self, validate=True):
        trigger_msg = self.msg
        tparams = trigger_msg.get('dispatcher', {})
        tparams["custom_encoder"] = self.custom_encoder
        tparams["custom_decoder"] = self.custom_decoder

        if not trigger_msg:
            raise ValueError('No trigger input to trigger task')

        if not self.dispatcher:
            if self.debug:
                self.dispatcher = dispatcher.Stdout(tparams)
            else:
                self.dispatcher = dispatcher.Http(tparams)

        self.meta = trigger_msg.get('meta') or {}

        self.trigger.webhook_url = self.dispatcher.webhook_url or ''

        if self.connection:
            params = (trigger_msg.get('connection') or {})
            self.connection.set(params)
            self.connection.connect(params)
            self.trigger.connection = self.connection

        input_data = self.trigger.input

        if input_data:
            input_data.set(trigger_msg.get('input'), validate)
