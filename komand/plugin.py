# -*- coding: utf-8 -*-
import logging
import io
import jsonschema
import pkg_resources
import json
import copy
import uuid
import inspect
import six

import komand.server
from .dispatcher import Stdout, Http
from .connection import ConnectionCache

from .exceptions import *

root_logger = logging.getLogger()
root_logger.setLevel('DEBUG')
root_logger.addHandler(logging.StreamHandler())

input_message_schema = json.load(
    pkg_resources.resource_stream(__name__, '/'.join(('data', 'input_message_schema.json'))))
output_message_schema = json.load(
    pkg_resources.resource_stream(__name__, '/'.join(('data', 'output_message_schema.json'))))


class Python2StringIO(io.StringIO):
    def write(self, s):
        if isinstance(s, str):
            s = s.decode('utf-8')
        super(Python2StringIO, self).write(s)


if six.PY2:
    stream_class = Python2StringIO
else:
    stream_class = io.StringIO


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

    def server(self, port=8001):
        server = komand.server.PluginServer(
            plugin=self,
            port=port,
            debug=self.debug,
            )

        server.start()

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
            'meta': input_message['body']['meta']
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

    @staticmethod
    def validate_json(json_object, schema):
        try:
            jsonschema.validate(json_object, schema)
        except jsonschema.exceptions.ValidationError as e:
            raise ClientException('input JSON was invalid', e)
        except Exception as e:
            raise Exception('Unable to validate input JSON', e)

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
            Plugin.validate_json(input_message, input_message_schema)
            message_type = input_message['type']
            if message_type not in ['action_start', 'trigger_start']:
                raise ClientException('Unsupported message type "{}"'.format(message_type))
            if message_type == 'action_start':
                out_type = 'action_event'
                output = self.handle_action_start(input_message['body'], logger, is_test, is_debug)
            elif message_type == 'trigger_start':
                out_type = 'trigger_event'
                output = self.handle_trigger_start(input_message['body'], logger, log_stream, is_test, is_debug)
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

    def handle_action_start(self, message_body, logger, is_test=False, is_debug=False):
        """
        Starts an action.
        :param message_body: The action_start message.
        :param is_test: True if the action's test method should execute
        :param is_debug: True if debug is enabled
        :return: An action_event message
        """

        action_name = message_body['action']
        if action_name not in self.actions:
            raise ClientException('Unknown action "{}"'.format(action_name))

        action = self.actions[action_name]

        connection = self.connection_cache.get(message_body['connection'])

        # Copy the action for thread safety.
        # This is necessary because the object itself contains state like connection and debug.
        step = copy.copy(action)

        step.debug = is_debug
        step.connection = connection
        step.logger = logger

        params = message_body['input']

        try:
            step.input.validate(params)
        except jsonschema.exceptions.ValidationError as e:
            raise ClientException('action input JSON was invalid', e)
        except Exception as e:
            raise Exception('Unable to validate action input JSON', e)

        if is_test:
            func = step.test
        else:
            func = step.run

        output = func(params)
        step.output.validate(output)

        return output

    def handle_trigger_start(self, message_body, logger, log_stream, is_test=False, is_debug=False):
        """
        Starts a trigger.
        :param message_body: The trigger_start message.
        :param is_test: True if the action's test method should execute
        :param is_debug: True if debug is enabled
        :return:
        """

        trigger_name = message_body['trigger']
        if trigger_name not in self.triggers:
            raise ClientException('Unknown trigger "{}"'.format(trigger_name))

        trigger = self.triggers[trigger_name]

        connection = self.connection_cache.get(message_body['connection'])

        # Copy the action for thread safety.
        # This is necessary because the object itself contains state like connection and debug.
        step = copy.copy(trigger)

        step.debug = is_debug
        step.connection = connection
        step.logger = logger
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

        try:
            step.input.validate(params)
        except jsonschema.exceptions.ValidationError as e:
            raise ClientException('action input JSON was invalid', e)
        except Exception as e:
            raise Exception('Unable to validate action input JSON', e)

        if is_test:
            func = step.test
        else:
            func = step.run

        # Backward compatibility with tests with missing params
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
