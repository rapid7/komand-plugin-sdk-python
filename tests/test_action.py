import unittest
from io import StringIO
import sys, os

from komand.action import Action, Task
from komand.connection import Connection
from komand.variables import Input
from komand.variables import Output

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class MyConnection(Connection):
    schema = {
            "type" : "object",
            "properties" : {
                "price" : {"type" : "number" },
                "name" : {"type" : "string"},
                }
            }

    def __init__(self):
        super(self.__class__, self).__init__(self.schema)
    
    def connect(self, params={}):
        return None


class StupidActionInput(Input):
    schema = {
            "type" : "object",
            "properties" : {
                "greeting" : {"type" : "string"},
                }
            }

    def __init__(self):
        super(self.__class__, self).__init__(schema=self.schema)


class StupidActionOutput(Output):
    schema = {
            "type" : "object",
            "required": ["price", "name"],
            "properties" : {
                "price" : {"type" : "number" },
                "name" : {"type" : "string"},
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

    def run(self):
        return { 'price': 1100, 'name': 'Jon' }

    def test(self):
        return { 'price': 100, 'name': 'Jon' }


class TestActionRunner(unittest.TestCase):

    def test_action_test_succeeds(self):

        task = Task(MyConnection(), StupidAction(), {
            'body': { 'action': 'stupid', 
                'input': {
                    'greeting': 'hello'
                    },
                'meta': { 'action_id': 12345 }, 
                }
            })

        task.test()

if __name__ == '__main__':
    unittest.main()

