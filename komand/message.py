# -*- coding: utf-8 -*-
import sys
import json


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

SUCCESS = 'ok'
ERROR = 'error'


def envelope(msg_type, body={}):
    return {
        'body': body,
        'type': msg_type,
        'version': VERSION,
    }


def action_start(action='', meta={}, input={}, connection={}):
    return envelope(ACTION_START, {
        'action': action,
        'meta': meta,
        'input': input,
        'connection': connection,
    })


def trigger_start(trigger='', meta={}, dispatcher={}, input={}, connection={}):
    return envelope(TRIGGER_START, {
        'trigger': trigger,
        'meta': meta,
        'input': input,
        'dispatcher': dispatcher,
        'connection': connection,
        })


def trigger_event(meta={}, output={}, log=""):
    return envelope(TRIGGER_EVENT, {'meta': meta, 'output': output, 'log': log})


def action_success(meta={}, output={}, log=""):
    return envelope(ACTION_EVENT, {'meta': meta, 'output': output, 'status': SUCCESS, 'log': log})


def action_error(meta={}, error='', log=""):
    err = "%s" % error
    return envelope(ACTION_EVENT, {'meta': meta, 'error': err, 'status': ERROR, 'log': log})


def validate_trigger_start(body):
    if not body:
        raise Exception('No body: %s' % body)

    if 'trigger' not in body:
        raise Exception('Missing trigger in %s' % body)

    if 'connection' not in body:
        body['connection'] = {}

    if 'dispatcher' not in body:
        body['dispatcher'] = {}

    if 'input' not in body:
        body['input'] = {}


def validate_action_start(body):
    if not body:
        raise Exception('No body: %s' % body)

    if 'action' not in body:
        raise Exception('Missing action in %s' % body)

    if 'connection' not in body:
        body['connection'] = {}
    if 'dispatcher' not in body:
        body['dispatcher'] = {}
    if 'input' not in body:
        body['input'] = {}


validators = {
    TRIGGER_START: validate_trigger_start,
    ACTION_START:  validate_action_start,
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
    if 'version' not in msg:
        raise Exception("No message version: %s" % msg)

    if msg['version'] != VERSION:
        raise Exception("Invalid version: %s in %s" % (msg['version'], msg))

    if 'type' not in msg:
        raise Exception("No message type: %s" % msg)

    if msg['type'] not in valid_types:
        raise Exception("Invalid type: %s in %s" % (msg['type'], msg))

    if 'body' not in msg:
        raise Exception("No message body: %s" % msg)

    validators[msg['type']](msg['body'])
