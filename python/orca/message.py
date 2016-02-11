import sys
import json
import util


# version
VERSION = 'v1'

# types
TRIGGER_START = 'trigger_start'
ACTION_START = 'action_start'

valid_types = [
    TRIGGER_START,
    ACTION_START,
]


def validateTriggerStart(body):
    if not body:
        raise Exception('No body: %s' % body)
    if not body.has_key('trigger'):
        raise Exception('Missing trigger in %s' % body)
    if not body.has_key('trigger_id'):
        raise Exception('Missing trigger_id in %s' % body)


def validateActionStart(body):
    if not body:
        raise Exception('No body: %s' % body)
    if not body.has_key('action'):
        raise Exception('Missing action in %s' % body)
    if not body.has_key('action_id'):
        raise Exception('Missing action_id in %s' % body)

validators = {
    TRIGGER_START: validateTriggerStart,
    ACTION_START:  validateActionStart,
}

def unmarshal(fd=sys.stdin):
    """Unmarshals a message"""
    try:
        msg = json.load(fd)
    except Exception as e:
        raise Exception("Invalid message json: %s" % e), None, util.trace(e)

    validate(msg)
    return msg


def validate(msg):
    """Validate the message is good"""
    if not msg.has_key('version'):
        raise Exception("No message version: %s" % msg)
    if msg['version'] != VERSION:
        raise Exception("Invalid version: %s in %s" % (msg['version'], msg))

    if not msg.has_key('type'):
        raise Exception("No message type: %s" % msg)

    if not msg['type'] in valid_types:
        raise Exception("Invalid type: %s in %s" % (msg['type'], msg))

    if not msg.has_key('body'):
        raise Exception("No message body: %s" % msg)

    validators[msg['type']](msg['body'])


# unmarshal()
