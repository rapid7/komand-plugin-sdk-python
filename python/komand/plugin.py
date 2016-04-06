import message
import actions
import triggers

class Plugin:
    """An Komand Plugin."""

    def __init__(self, name, vendor, description, version):
        self.name = ""
        self.vendor = ""
        self.description = ""
        self.version = ""
        self._triggers = {}
        self._actions = {}

    def _lookup(self, msg):
        if msg.Type == TRIGGER_START:
            trig = self._trigger(msg)
            return triggers.Task(trig, msg) 
        elif msg.Type == ACTION_START:
            act = self._action(msg)
            return actions.Task(trig, msg) 
        else:
            raise Exception("Invalid message type:" + msg.Type)

    def run(self):
        """Run the plugin."""
        msg = message.unmarshal(stdin)
        runner = self._lookup(msg)
        runner.Run()

    def test(self):
        """Test the plugin."""
        msg = message.unmarshal(stdin)
        runner = self._lookup(msg)
        runner.Test()

    def add_trigger(self, trigger):
        """ add a new trigger """
        validateTrigger(trigger)
        self._triggers[trigger.name] = trigger

    def add_action(self, action):
        """ add a new action """
        validateAction(action)
        self._actions[action.name] = action

    def _trigger(self, msg):
        """Run the trigger"""
        trig = self._triggers.get(msg['trigger'])
        if not trig:
            raise Exception("Trigger missing: %s" % msg['trigger'])

    def _action(self, msg):
        """Run the action"""
        act = self._actions.get(msg['action'])
        if not trig:
            raise Exception("Action missing: %s" % msg['action'])



def validateTrigger(trigger):
    return

def validateAction(action):
    return
