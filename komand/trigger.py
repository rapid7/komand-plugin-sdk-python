import message
import dispatcher
import logging
import variables
import sys

class Trigger(object):
    """A trigger"""
    def __init__(self, name, description, input, output):
        self.name = name 
        self.description = description 
        self.connection = None
        self._sender = None
        self.input = input
        self.output = output

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
    def __init__(self, connection, trigger, msg, dispatch=None):
        self.connection = connection 
        self.trigger = trigger
        self.msg = msg
        self.dispatcher = dispatch
        self.meta = None

    def send(self, output):
        msg = message.TriggerEvent(meta=self.meta, output=output)
        self.dispatcher.write(msg)

    def test(self):
        """ Run test """
        dispatch = dispatcher.Stdout()

        try:
            self._setup()
            params = {}
            if self.trigger and self.trigger.input.parameters:
                params = self.trigger.input.parameters

            output = self.trigger.test(params)
        except Exception as e:
            logging.exception('trigger test failure: %s', e)
            return False

        msg = message.TriggerEvent(meta=self.meta, output=output)
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
        except:
            e = sys.exc_info()[0]
            logging.exception('trigger test failure: %s', e)
            # XXX: exit code??
            return


    def _setup(self):
        trigger_msg = self.msg

        if not trigger_msg:
            raise ValueError('No trigger input to trigger task')

        if not self.dispatcher:
            self.dispatcher = dispatcher.Http(trigger_msg.get('dispatcher') or {})

        self.meta = trigger_msg.get('meta') or {}

        if self.connection:
            params = (trigger_msg.get('connection') or {})
            self.connection.set(params)
            self.connection.connect(params)
            self.trigger.connection = self.connection

        input = self.trigger.input

        if input:
            input.set(trigger_msg.get('input'))

