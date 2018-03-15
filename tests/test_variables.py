import unittest
import sys, os
from komand.variables import Input

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestMessage(unittest.TestCase):

    def test_input_sample(self):
        schema = {
            "type" : "object",
            "properties": {
                "foo": {
                    "type": "string"
                },
                "bar": {
                    "type": "integer"
                },
            }
        }

        i = Input(schema)
        print(i.sample())


if __name__ == '__main__':
    unittest.main()
