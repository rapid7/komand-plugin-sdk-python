# -*- coding: utf-8 -*-
import logging
import io
import jsonschema
import pkg_resources
import json

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

    def handle_step(self, input_message, is_test=False, is_debug=False):
        """
        Executes a single step, given the input message dictionary.
        :param input_message: The input message
        :param is_test: Whether or not this is
        :param is_debug:
        :return:
        """

        log_stream = io.StringIO()
        stream_handler = logging.StreamHandler(log_stream)
        logger.addHandler(stream_handler)

        output = None
        success = True
        error_message = None

        try:
            try:
                jsonschema.validate(input_message, input_message_schema)
            except jsonschema.exceptions.ValidationError as e:
                raise ClientException('input JSON was invalid', e)
            except Exception as e:
                raise Exception('Unable to validate input JSON', e)

            message_type = input_message['type']
            if message_type == 'action_start':
                output_message_type = 'action_event'
                output = StepHandler.handle_action_start(self, input_message['body'], is_test, is_debug)
            elif message_type == 'trigger_start':
                StepHandler.handle_trigger_start(self, input_message['body'], is_test, is_debug)
            else:
                output = None
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

            log = log_stream.getvalue()

            output_message = {
                'log': log,
                'status': 'ok' if success else 'error',
                'meta': input_message['meta']
            }
            if success:
                output_message['output'] = output
            else:
                output_message['error'] = error_message

    def handle_action_start(self, message_body, is_test=False, is_debug=False):
        action_name = message_body['action']
        if action_name not in self.plugin.actions:
            raise ClientException('Unknown action "{}"'.format(action_name))

        action = self.plugin.actions[action_name]
        params = message_body['input']

        action.debug = is_debug
        action.plugin.connection = message_body['connection']

        if is_test:
            func = action.test
        else:
            func = action.run

        output = func(params)

        return output

    def handle_trigger_start(self, message_body, is_test=False, is_debug=False):
        trigger_name = message_body['trigger']
        if trigger_name not in self.plugin.triggers:
            raise ClientException('Unknown trigger "{}"'.format(trigger_name))

        return


StepHandler.handle_step({})
