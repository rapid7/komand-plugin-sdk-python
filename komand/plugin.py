import komand.message as message
import komand.action as action
import komand.trigger as trigger
import sys
import komand.dispatcher as dispatcher

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class Plugin(object):
    """An Komand Plugin."""

    def __init__(self, name='', vendor='', description='', version='', connection=None, custom_encoder=None, custom_decoder=None):
        self.name = name
        self.vendor = vendor
        self.description = description
        self.version = version
        self.connection = connection
        self.triggers = {}
        self.actions = {}
        self.debug = False
        self.custom_decoder = custom_decoder
        self.custom_encoder = custom_encoder

    def _lookup(self, msg):
        if msg['type'] == message.TRIGGER_START:
            trig = self._trigger(msg['body'])
            return trigger.Task(
                connection=self.connection,
                trigger=trig,
                msg=msg['body'],
                custom_encoder=self.custom_encoder,
                custom_decoder=self.custom_decoder)
        elif msg['type'] == message.ACTION_START:
            act = self._action(msg['body'])
            return action.Task(
                connection=self.connection,
                action=act,
                msg=msg['body'],
                custom_encoder=self.custom_encoder,
                custom_decoder=self.custom_decoder)
        else:
            raise Exception("Invalid message type:" + msg.Type)

    def run(self, msg=None):
        """Run the plugin."""
        input = sys.stdin
        if msg:
            input = StringIO(msg)

        msg = message.unmarshal(input, cd=self.custom_decoder)
        runner = self._lookup(msg)
        if self.debug:
            runner.debug = True

        runner.run()

    def test(self, msg=None):
        """Test the plugin."""
        input = sys.stdin
        if msg:
            input = StringIO(msg)

        msg = message.unmarshal(input, cd=self.custom_decoder)

        if not msg:
            msg = message.unmarshal(sys.stdin)
        runner = self._lookup(msg)

        if not runner.test():
            return sys.exit(1)

    def add_trigger(self, trigger):
        """ add a new trigger """
        self.triggers[trigger.name] = trigger

    def add_action(self, action):
        """ add a new action """
        self.actions[action.name] = action

    def _trigger(self, msg):
        """Run the trigger"""
        trig = self.triggers.get(msg['trigger'])
        if not trig:
            raise Exception("Trigger missing: %s" % msg['trigger'])
        return trig

    def _action(self, msg):
        """Run the action"""
        act = self.actions.get(msg['action'])
        if not act:
            raise Exception("Action missing: %s" % msg['action'])
        return act
