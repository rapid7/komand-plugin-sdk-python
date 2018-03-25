import pytest
from io import StringIO
import komand.message


def test_ok_message():
    sample = u'{ "meta": { "test": "this" }, "body": {"trigger": "hello123"}, "version": "v1", "type": "trigger_start" }'
    fd = StringIO(sample)
    m = komand.message.unmarshal(fd)
    print(m)


def test_invalid_message_fails():
    sample = u'{ "hello": "there" }'
    fd = StringIO(sample)
    with pytest.raises(Exception):
        komand.message.unmarshal(fd)
