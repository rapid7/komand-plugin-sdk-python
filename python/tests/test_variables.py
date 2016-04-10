import unittest
from StringIO import StringIO
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

      input = komand.Input(schema)
      print input.sample()


if __name__ == '__main__':
    unittest.main()

