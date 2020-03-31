from insightconnect_plugin_runtime.trigger import Trigger
from insightconnect_plugin_runtime.connection import Connection
from insightconnect_plugin_runtime.variables import Input, Output


def test_trigger_test_succeeds():
    class MyConnection(Connection):
        schema = {
            "type": "object",
            "properties": {"price": {"type": "number"}, "name": {"type": "string"},},
        }

        def __init__(self):
            super(self.__class__, self).__init__(self.schema)

        def connect(self, params={}):
            return None

    class StupidTriggerInput(Input):
        schema = {"type": "object", "properties": {"greeting": {"type": "string"},}}

        def __init__(self):
            super(self.__class__, self).__init__(schema=self.schema)

    class StupidTriggerOutput(Output):
        schema = {
            "type": "object",
            "required": ["price", "name"],
            "properties": {"price": {"type": "number"}, "name": {"type": "string"},},
        }

        def __init__(self):
            super(self.__class__, self).__init__(schema=self.schema)

    class StupidTrigger(Trigger):
        def __init__(self):
            super(self.__class__, self).__init__(
                "stupid", "an action", StupidTriggerInput(), StupidTriggerOutput(),
            )

        def run(self, params={}):
            return {"price": 1100, "name": "Jon"}

        def test(self, params={}):
            return {"price": 100, "name": "Jon"}
