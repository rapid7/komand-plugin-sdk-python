import message
import action
import trigger

class Plugin(object):
    """An Komand Plugin."""

    def __init__(self, name='', vendor='', description='', version=''):
        self.name = name 
        self.vendor = vendor 
        self.description = description 
        self.version = version 
        self.triggers = {}
        self.actions = {}

    def _lookup(self, msg):
        if msg.Type == TRIGGER_START:
            trig = self._trigger(msg)
            return trigger.Task(self, trig, msg) 
        elif msg.Type == ACTION_START:
            act = self._action(msg)
            return action.Task(self, trig, msg) 
        else:
            raise Exception("Invalid message type:" + msg.Type)

    def run(self):
        """Run the plugin."""
        msg = message.unmarshal(stdin)
        runner = self._lookup(msg)
        runner.run()

    def connection(self):
        """ Override to define a connection"""
        raise NotImplementedError 

    def test(self):
        """Test the plugin."""
        msg = message.unmarshal(stdin)
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

    def _action(self, msg):
        """Run the action"""
        act = self.actions.get(msg['action'])
        if not trig:
            raise Exception("Action missing: %s" % msg['action'])
