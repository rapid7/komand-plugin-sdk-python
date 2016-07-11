import message
import action
import trigger
import sys
import dispatcher


class Plugin(object):
    """An Komand Plugin."""

    def __init__(self, name='', vendor='', description='', version='', connection=None):
        self.name = name 
        self.vendor = vendor 
        self.description = description 
        self.version = version 
        self.connection = connection
        self.triggers = {}
        self.actions = {}
        self.debug = False

    def _lookup(self, msg):
        if msg['type'] == message.TRIGGER_START:
            trig = self._trigger(msg['body'])
            return trigger.Task(
                    connection=self.connection, 
                    trigger=trig, 
                    msg=msg['body']) 
        elif msg['type'] == message.ACTION_START:
            act = self._action(msg['body'])
            return action.Task(
                    connection=self.connection, 
                    action=act, 
                    msg=msg['body']) 
        else:
            raise Exception("Invalid message type:" + msg.Type)

    def run(self):
        """Run the plugin."""
        msg = message.unmarshal(sys.stdin)
        runner = self._lookup(msg)
        if self.debug:
            runner.dispatcher = dispatcher.Stdout()

        runner.run()

    def test(self):
        """Test the plugin."""
        msg = message.unmarshal(sys.stdin)
        runner = self._lookup(msg)
        runner.test()

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
