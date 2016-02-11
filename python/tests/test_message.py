import unittest
from StringIO import StringIO
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import orca.message 

class TestMessage(unittest.TestCase):

  def test_invalid_message_fails(self):
      sample = '{ "hello": "there" }'
      fd = StringIO(sample)
      with self.assertRaises(Exception):
        orca.message.unmarshal(fd)

if __name__ == '__main__':
    unittest.main()

