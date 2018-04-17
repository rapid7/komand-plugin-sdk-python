from komand.action import Action
from komand.connection import Connection
from komand.variables import Input, Output


def test_action_test_succeeds():

    class MyConnection(Connection):
        schema = {
            "type": "object",
            "properties": {
                "price": {
                    "type": "number"
                },
                "name": {
                    "type": "string"
                },
            }
        }

        def __init__(self):
            super(self.__class__, self).__init__(self.schema)

        def connect(self, params={}):
            return None

    class StupidActionInput(Input):
        schema = {
            "type": "object",
            "properties": {
                "greeting": {
                    "type": "string"
                },
            }
        }

        def __init__(self):
            super(self.__class__, self).__init__(schema=self.schema)

    class StupidActionOutput(Output):
        schema = {
            "type": "object",
            "required": ["price", "name"],
            "properties": {
                "price": {
                    "type": "number"
                },
                "name": {
                    "type": "string"
                },
            }
        }

        def __init__(self):
            super(self.__class__, self).__init__(schema=self.schema)

    class StupidAction(Action):
        def __init__(self):
            super(self.__class__, self).__init__(
                'stupid',
                'an action',
                StupidActionInput(),
                StupidActionOutput(),
            )

        def run(self, params={}):
            return {'price': 1100, 'name': 'Jon'}

        def test(self, params={}):
            return {'price': 100, 'name': 'Jon'}
