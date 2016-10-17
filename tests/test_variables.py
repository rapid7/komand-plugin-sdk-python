import unittest
from io import StringIO
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import komand.variables 

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

      i = komand.Input(schema)
      print(i.sample())


if __name__ == '__main__':
    unittest.main()

