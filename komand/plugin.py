# -*- coding: utf-8 -*-
import copy
import inspect
import io
import json
import logging

import jsonschema
import six
import uuid

from .connection import ConnectionCache
from .dispatcher import Stdout, Http
from .exceptions import ClientException, ServerException, LoggedException
from .schema import input_message_schema


class Python2StringIO(io.StringIO):
    """
    Python2 compatible StringIO class.

    This was a hack to get log saving to work.
    There's definitely a better solution.
    """

    def write(self, s):
        if isinstance(s, str):
            s = s.decode('utf-8')
        super(Python2StringIO, self).write(s)


if six.PY2:
    stream_class = Python2StringIO
else:
    stream_class = io.StringIO

message_output_type = {
    'action_start': 'action_event',
    'trigger_start': 'trigger_event',
}


class Plugin(object):
    """A Komand Plugin."""

    def __init__(self, name='', vendor='', description='', version='', connection=None, custom_encoder=None,
                 custom_decoder=None):
        self.name = name
        self.vendor = vendor
        self.description = description
        self.version = version
        self.connection = connection
        self.connection_cache = ConnectionCache(connection)
        self.triggers = {}
        self.actions = {}
        self.debug = False
        self.custom_decoder = custom_decoder
        self.custom_encoder = custom_encoder

    def add_trigger(self, trigger):
        """ add a new trigger """
        self.triggers[trigger.name] = trigger

    def add_action(self, action):
        """ add a new action """
        self.actions[action.name] = action

    @staticmethod
    def envelope(message_type, input_message, log, success, output, error_message):
        """
        Creates an output message of a step's execution.

        :param message_type: The message type
        :param input_message: The input message
        :param log: The log of the step, as a single string
        :param success: whether or not the step was successful
        :param output: The step data output
        :param error_message: An error message if an error was thrown
        :return: An output message
        """

        output_message = {
            'log': log,
            'status': 'ok' if success else 'error',
            'meta': input_message['body'].get('meta', None)
        }
        if success:
            output_message['output'] = output
        else:
            output_message['error'] = error_message
        return {
            'body': output_message,
            'version': 'v1',
            'type': message_type
        }

    def marshal(self, msg, fd):
        """ Marshal a message to fd. """

        if self.custom_encoder is None:
            json.dump(msg, fd)
        else:
            json.dump(msg, fd, cls=self.custom_encoder)
        fd.flush()

    def unmarshal(self, fd):
        """ Unmarshal a message. """

        if self.custom_decoder is None:
            msg = json.load(fd)
        else:
            msg = json.load(fd, cls=self.custom_decoder)
        return msg

    @staticmethod
    def validate_json(json_object, schema):
        try:
            jsonschema.validate(json_object, schema)
        except jsonschema.exceptions.ValidationError as e:
            raise ClientException('input JSON was invalid', e)
        except Exception as e:
            raise Exception('Unable to validate input JSON', e)

    @staticmethod
    def validate_input_message(input_message):
        if input_message is None:
            raise ClientException('Input message was None')
        if not isinstance(input_message, dict):
            raise ClientException('Input message is not a dictionary')
        if 'type' not in input_message:
            raise ClientException('"type" missing from input message')
        if 'version' not in input_message:
            raise ClientException('"version" missing from input message')
        if 'body' not in input_message:
            raise ClientException('"body" missing from input message')

        version = input_message['version']
        type = input_message['type']
        body = input_message['body']

        if version != 'v1':
            raise ClientException('Unsupported version %s. Only v1 is supported'.format(version))
        if type == 'action_start':
            if 'action' not in body:
                raise ClientException('Message is action_start but field "action" is missing from body')
            if not isinstance(body['action'], str):
                raise ClientException('Action field must be a string')
        elif type == 'trigger_start':
            if 'trigger' not in body:
                raise ClientException('Message is trigger_start but field "trigger" is missing from body')
            if not isinstance(body['trigger'], str):
                raise ClientException('Trigger field must be a string')
        else:
            raise ClientException('Unsupported message type %s. Must be action_start or trigger_start')
        if 'meta' not in body:
            raise ClientException('Field "meta" missing from body')

        # This is existing behavior.
        if 'connection' not in body:
            body['connection'] = {}
        if 'dispatcher' not in body:
            body['dispatcher'] = {}
        if 'input' not in body:
            body['input'] = {}

    def handle_step(self, input_message, is_test=False, is_debug=False):
        """
        Executes a single step, given the input message dictionary.

        Execution of this method is designed to be thread safe.

        :param input_message: The input message
        :param is_test: Whether or not this is
        :param is_debug:
        :return:
        """

        request_id = uuid.uuid4()
        log_stream = stream_class()
        stream_handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger('step_handler_{}'.format(request_id))
        logger.setLevel('DEBUG' if is_debug else 'INFO')
        logger.addHandler(stream_handler)

        success = True
        ex = None
        output = None
        out_type = None

        try:

            # Attempt to grab message type first
            message_type = input_message.get('type')
            out_type = message_output_type.get(message_type)
            if message_type not in ['action_start', 'trigger_start']:
                raise ClientException('Unsupported message type "{}"'.format(message_type))

            Plugin.validate_input_message(input_message)

            if message_type == 'action_start':
                out_type = 'action_event'
                output = self.start_step(input_message['body'], 'action', logger, log_stream, is_test, is_debug)
            elif message_type == 'trigger_start':
                out_type = 'trigger_event'
                output = self.start_step(input_message['body'], 'trigger', logger, log_stream, is_test, is_debug)
        except ClientException as e:
            success = False
            ex = e
            logger.exception(e)
        except ServerException as e:
            success = False
            ex = e
            logger.exception(e)
        except Exception as e:
            success = False
            ex = e
            logger.exception(e)
        finally:
            output = Plugin.envelope(out_type, input_message, log_stream.getvalue(), success, output,
                                     str(ex))
            if not success:
                raise LoggedException(ex, output)
            return output

    def start_step(self, message_body, step_key, logger, log_stream, is_test=False, is_debug=False):
        """
        Starts an action.
        :param message_body: The action_start message.
        :param step_key: The type of step to execute
        :param logger the logger for logging
        :param log_stream the raw stream for the log
        :param is_test: True if the action's test method should execute
        :param is_debug: True if debug is enabled
        :return: An action_event message
        """

        action_name = message_body[step_key]
        dictionary = getattr(self, step_key + 's')
        if action_name not in dictionary:
            raise ClientException('Unknown {} "{}"'.format(step_key, action_name))
        action = dictionary[action_name]

        connection = self.connection_cache.get(message_body['connection'])

        # Copy the action for thread safety.
        # This is necessary because the object itself contains stateful fields like connection and debug.
        step = copy.copy(action)

        step.debug = is_debug
        step.connection = connection
        step.logger = logger

        # Extra setup for triggers
        if step_key == 'trigger':
            step.log_stream = log_stream
            step.meta = message_body['meta']
            step.webhook_url = message_body['dispatcher']['webhook_url']
            step.url = message_body['dispatcher']['url']

            if not step.dispatcher:
                if step.debug:
                    step.dispatcher = Stdout(message_body['dispatcher'])
                else:
                    step.dispatcher = Http(message_body['dispatcher'])

        params = message_body['input']

        # Validate input message
        try:
            step.input.validate(params)
        except jsonschema.exceptions.ValidationError as e:
            raise ClientException('{} input JSON was invalid'.format(step_key), e)
        except Exception as e:
            raise Exception('Unable to validate {} input JSON'.format(step_key), e)

        if is_test:
            func = step.test
        else:
            func = step.run

        # Backward compatibility with steps with missing argument params
        # The SDK has always defined the signature of the run/test methods to include the params dictionary.
        # However, the code generation generates the test method without the params argument.
        if six.PY2:
            argspec = inspect.getargspec(func)
            if len(argspec.args) > 1:
                output = func(params)
            else:
                output = func()
        else:
            parameters = inspect.signature(func)
            if len(parameters.parameters) > 0:
                output = func(params)
            else:
                output = func()

        step.output.validate(output)

        return output
