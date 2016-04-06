import message
import dispatcher
import logging
import variables

class Trigger(object):
    """A trigger"""
    def __init__(self, name, description):
        self.name = name 
        self.description = description 
        self.inputs = {}
        self.connection = None
        self._sender = None

    def send(self, event):
        schema = self.output()
        if schema:
          event = schema.validate(event)

        self._sender.send(event)

    def input(self):
        """ Return input schema for trigger """
        raise NotImplementedError

    def output(self):
        """ Return output schema for trigger """
        raise NotImplementedError

    def run(self):
        """ Run a trigger. Returns nothing """
        raise NotImplementedError

    def test(self):
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

    def send(self, msg):
        msg = message.TriggerEvent(meta=self.meta, output=output)
        self.dispatcher.write(msg)

    def test(self):
        """ Run test """
        dispatcher = dispatcher.Stdout()

        try:
            self._setup()
            output = self.trigger.test()
        except Exception as e:
            logging.exception('trigger test failure: %s', e)
            return False

        msg = message.TriggerEvent(meta=self.meta, output=output)
        dispatcher.write(msg)
        return True

    def run(self):
        """ Run the trigger"""
        try:
            self._setup()
            self.trigger._sender = self
            self.trigger.run()
        except Error as e:
           logging.exception('trigger test failure: %s', e)
            # XXX: exit code??
           return


    def _setup(self):
        trigger_msg = self.msg.get('body')

        if not trigger_msg:
            raise ValueError('No trigger input to trigger task')

        if not self.dispatcher:
            self.dispatcher = dispatcher.Http(trigger_msg.get('dispatcher') or {})

        self.meta = trigger_msg.get('meta') or {}

        if self.connection:
            params = (trigger_msg.get('connection') or {})
            self.connection.set(params)
            self.connection.connect()
            self.trigger.connection = self.connection

        input = self.trigger.input()

        if input:
            inputs = input.validate(trigger_msg.get('input'))
            self.trigger.inputs = inputs

