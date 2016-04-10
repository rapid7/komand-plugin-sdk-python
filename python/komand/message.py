import sys
import json
import util


# version
VERSION = 'v1'

# types
TRIGGER_START = 'trigger_start'
ACTION_START = 'action_start'
TRIGGER_EVENT = 'trigger_event'
ACTION_EVENT = 'action_event'

valid_types = [
    TRIGGER_START,
    ACTION_START,
]

SUCCESS = 'ok';
ERROR = 'error';

def envelope(msg_type, body={}):
    return {
            'body': body,
            'type': msg_type,
            'version': VERSION,
            }

def ActionStart(action='', meta={}, input={}, connection={}):
     return envelope(ACTION_START, { 
         'action': action,
         'meta': meta,
         'input': input,
         'connection': connection,
         }) 
        

def TriggerStart(trigger='', meta={}, dispatcher={}, input={}, connection={}):
     return envelope(TRIGGER_START, { 
         'trigger': trigger,
         'meta': meta,
         'input': input,
         'dispatcher': dispatcher,
         'connection': connection,
         }) 
        

def TriggerEvent(meta={}, output={}):
    return envelope(TRIGGER_EVENT, { 'meta': meta, 'output': output });

def ActionSuccess(meta={}, output={}):
    return envelope(ACTION_EVENT, { 'meta': meta, 'output': output, 'status': SUCCESS });

def ActionError(meta={}, error=''):
    err = "%s" % error
    return envelope(ACTION_EVENT, { 'meta': meta, 'error': err, 'status': ERROR });

def validateTriggerStart(body):
    if not body:
        raise Exception('No body: %s' % body)
    if not body.has_key('trigger'):
        raise Exception('Missing trigger in %s' % body)

    if not body.has_key('connection'):
        body['connection'] = {}
    if not body.has_key('dispatcher'):
        body['dispatcher'] = {}
    if not body.has_key('input'):
        body['input'] = {}


def validateActionStart(body):
    if not body:
        raise Exception('No body: %s' % body)
    if not body.has_key('action'):
        raise Exception('Missing action in %s' % body)

    if not body.has_key('connection'):
        body['connection'] = {}
    if not body.has_key('dispatcher'):
        body['dispatcher'] = {}
    if not body.has_key('input'):
        body['input'] = {}


validators = {
    TRIGGER_START: validateTriggerStart,
    ACTION_START:  validateActionStart,
}

def marshal(msg, fd=sys.stdout):
    """ Marshal a message to fd"""
    json.dump(msg, fd)
    fd.flush()

def marshal_string(msg):
    """ Marshal a message to a string"""
    return json.dumps(msg)

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
