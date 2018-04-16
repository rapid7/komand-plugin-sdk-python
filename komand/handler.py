# -*- coding: utf-8 -*-
import logging
import io
import jsonschema
import pkg_resources
import json
import copy
import komand.dispatcher as dispatcher

root_logger = logging.getLogger()
root_logger.setLevel('INFO')
root_logger.addHandler(logging.StreamHandler())

logger = logging.getLogger('step_handler')
logger.setLevel('INFO')

input_message_schema = json.load(
    pkg_resources.resource_stream(__name__, '/'.join(('data', 'input_message_schema.json'))))
output_message_schema = json.load(
    pkg_resources.resource_stream(__name__, '/'.join(('data', 'output_message_schema.json'))))


class ClientException(Exception):
    """
    An exception which marks an error made by the plugin invoker.

    Some examples of when to use this are:
    - Malformed/Incorrect input data
    - External HTTP server throws a 400 level error

    """
    pass


class ServerException(Exception):
    """
    An Exception which marks an error made by an external server.

    Some examples of when to use this are:
    - External server throws a 500 Error

    """
    pass


class StepHandler:

    def __init__(self, plugin):
        self.plugin = plugin

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

    def handle_step(self, input_message, is_test=False, is_debug=False):
        """
        Executes a single step, given the input message dictionary.

        Execution of this method is designed to be thread safe.

        :param input_message: The input message
        :param is_test: Whether or not this is
        :param is_debug:
        :return:
        """

        log_stream = io.StringIO()
        stream_handler = logging.StreamHandler(log_stream)
        logger.addHandler(stream_handler)

        success = True
        error_message = None
        message_type = None

        try:
            try:
                jsonschema.validate(input_message, input_message_schema)
            except jsonschema.exceptions.ValidationError as e:
                raise ClientException('input JSON was invalid', e)
            except Exception as e:
                raise Exception('Unable to validate input JSON', e)

            message_type = input_message['type']

            if message_type not in ['action_start', 'trigger_start']:
                raise ClientException('Unsupported message type "{}"'.format(message_type))

        except ClientException as e:
            success = False
            error_message = str(e)
            logger.exception(e)
        except ServerException as e:
            success = False
            error_message = str(e)
            logger.exception(e)
        except Exception as e:
            success = False
            error_message = str(e)
            logger.exception(e)
        finally:
            if not success:
                return StepHandler.envelope(None, input_message, log_stream.getvalue(), success, None, error_message)

        if message_type == 'action_start':

            output = None

            try:
                output = StepHandler.handle_action_start(self, input_message['body'], is_test, is_debug)
            except ClientException as e:
                success = False
                error_message = str(e)
                logger.exception(e)
            except ServerException as e:
                success = False
                error_message = str(e)
                logger.exception(e)
            except Exception as e:
                success = False
                error_message = str(e)
                logger.exception(e)
            finally:
                return StepHandler.envelope('action_event', input_message, log_stream.getvalue(), success, output, error_message)

        elif message_type == 'trigger_start':
            try:
                StepHandler.handle_trigger_start(self, input_message['body'], is_test, is_debug)
            except ClientException as e:
                success = False
                error_message = str(e)
                logger.exception(e)
            except ServerException as e:
                success = False
                error_message = str(e)
                logger.exception(e)
            except Exception as e:
                success = False
                error_message = str(e)
                logger.exception(e)
            finally:
                if not success:
                    return StepHandler.envelope(None, input_message, log_stream.getvalue(), success, None, error_message)

    def handle_action_start(self, message_body, is_test=False, is_debug=False):
        """
        Starts an action.
        :param message_body: The action_start message.
        :param is_test: True if the action's test method should execute
        :param is_debug: True if debug is enabled
        :return: An action_event message
        """

        action_name = message_body['action']
        if action_name not in self.plugin.actions:
            raise ClientException('Unknown action "{}"'.format(action_name))

        action = self.plugin.actions[action_name]

        # Copy the action for thread safety.
        # This is necessary because the object itself contains state like connection and debug.
        step = copy.copy(action)

        step.debug = is_debug
        step.connection = message_body['connection']

        params = message_body['input']

        if is_test:
            func = step.test
        else:
            func = step.run

        output = func(params)

        return output

    def handle_trigger_start(self, message_body, is_test=False, is_debug=False):
        """
        Starts a trigger.
        :param message_body: The trigger_start message.
        :param is_test: True if the action's test method should execute
        :param is_debug: True if debug is enabled
        :return:
        """

        trigger_name = message_body['trigger']
        if trigger_name not in self.plugin.triggers:
            raise ClientException('Unknown trigger "{}"'.format(trigger_name))

        trigger = self.plugin.triggers[trigger_name]

        # Copy the action for thread safety.
        # This is necessary because the object itself contains state like connection and debug.
        step = copy.copy(trigger)

        step.debug = is_debug
        step.connection = message_body['connection']
        step.meta = message_body['meta']

        step.webhook_url = message_body['dispatcher']['webhook_url']
        step.url = message_body['dispatcher']['url']

        if not step.dispatcher:
            if step.debug:
                step.dispatcher = dispatcher.Stdout(message_body['dispatcher'])
            else:
                step.dispatcher = dispatcher.Http(message_body['dispatcher'])

        params = message_body['input']

        if is_test:
            func = step.test
        else:
            func = step.run

        func(params)
