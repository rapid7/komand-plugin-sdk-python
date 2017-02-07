import sys
import json
import komand.util as util


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
    if not 'trigger' in body:
        raise Exception('Missing trigger in %s' % body)

    if not 'connection' in body:
        body['connection'] = {}
    if not 'dispatcher' in body:
        body['dispatcher'] = {}
    if not 'input' in body:
        body['input'] = {}


def validateActionStart(body):
    if not body:
        raise Exception('No body: %s' % body)
    if not 'action' in body:
        raise Exception('Missing action in %s' % body)

    if not 'connection' in body:
        body['connection'] = {}
    if not 'dispatcher' in body:
        body['dispatcher'] = {}
    if not 'input' in body:
        body['input'] = {}


validators = {
    TRIGGER_START: validateTriggerStart,
    ACTION_START:  validateActionStart,
}

def marshal(msg, fd=sys.stdout, ce=None):
    """ Marshal a message to fd"""
    if ce is None:
        json.dump(msg, fd)
    else:
        json.dump(msg, fd, cls=ce)
    fd.flush()

def marshal_string(msg, ce=None):
    """ Marshal a message to a string"""
    if ce is None:
        return json.dumps(msg)
    else:
        return json.dumps(msg, cls=ce)

def unmarshal(fd=sys.stdin, cd=None):
    """Unmarshals a message"""
    try:
        msg = None
        if cd is None:
            msg = json.load(fd)
        else:
            msg = json.load(fd, cls=cd)
    except Exception as e:
        raise Exception("Invalid message json: %s" % e)

    validate(msg)
    return msg


def validate(msg):
    """Validate the message is good"""
    if not 'version' in msg:
        raise Exception("No message version: %s" % msg)
    if msg['version'] != VERSION:
        raise Exception("Invalid version: %s in %s" % (msg['version'], msg))

    if not 'type' in msg:
        raise Exception("No message type: %s" % msg)

    if not msg['type'] in valid_types:
        raise Exception("Invalid type: %s in %s" % (msg['type'], msg))

    if not 'body' in msg:
        raise Exception("No message body: %s" % msg)

    validators[msg['type']](msg['body'])


# unmarshal()
