import unittest
from io import StringIO
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import komand.message 

class TestMessage(unittest.TestCase):

  def test_ok_message(self):
      sample = '{ "meta": { "test": "this" }, "body": {"trigger": "hello123"}, "version": "v1", "type": "trigger_start" }'
      fd = StringIO(sample)
      m = komand.message.unmarshal(fd)
      print(m)


  def test_invalid_message_fails(self):
      sample = '{ "hello": "there" }'
      fd = StringIO(sample)
      with self.assertRaises(Exception):
        komand.message.unmarshal(fd)

if __name__ == '__main__':
    unittest.main()

