# -*- coding: utf-8 -*-
import copy
import inspect
import io
import json
import logging

import jsonschema
import uuid

from .connection import ConnectionCache
from .dispatcher import Stdout, Http
from .exceptions import ClientException, ServerException, LoggedException


message_output_type = {
    "action_start": "action_event",
    "trigger_start": "trigger_event",
}


class Workflow(object):
    def __init__(
        self,
        shortOrgId=None,
        orgProductToken=None,
        uiHostUrl=None,
        jobId=None,
        stepId=None,
        versionId=None,
        nextStepId=None,
        nextEdgeId=None,
        triggerId=None,
        jobExecutionContextId=None,
        time=None,
        connectionTestId=None,
        connectionTestTimeout=None,
        workflowId=None,
    ):
        """
        Worflow object for the Meta Class
        :param shortOrgId: Short version of the Organization ID
        :param orgProductToken: Organization Product Token
        :param uiHostUrl: Job URL for triggers
        :param jobId: Job UUID
        :param stepId: Step UUID
        :param versionId:  Workflow Version UUID
        :param nextStepId: Next Step UUID
        :param nextEdgeId: Next Edge UUID
        :param triggerId: Trigger UUID
        :param jobExecutionContextId: Job Execution Context UUID
        :param time: Time the action or trigger was executed
        :param connectionTestId: Connection Test ID
        :param connectionTestTimeout: Connection Test Timeout
        :param workflowId: Workflow ID
        """
        self.shortOrgId = shortOrgId
        self.orgProductToken = orgProductToken
        self.uiHostUrl = uiHostUrl
        self.jobId = jobId
        self.stepId = stepId
        self.versionId = versionId
        self.nextStepId = nextStepId
        self.nextEdgeId = nextEdgeId
        self.triggerId = triggerId
        self.jobExecutionContextId = jobExecutionContextId
        self.time = time
        self.connectionTestId = connectionTestId
        self.connectionTestTimeout = connectionTestTimeout
        self.workflowId = workflowId

    @classmethod
    def from_komand(cls, input_message):
        """Creates a Workflow object from Komand"""
        return cls(
            workflowId=input_message.get("workflow_uid", None),
            stepId=input_message.get("step_uid", None),
            versionId=input_message.get("workflow_version_uid", None),
        )

    @classmethod
    def from_insight_connect(cls, input_message):
        """Creates a Workflow object from Insight Connect"""
        return cls(
            shortOrgId=input_message.get("shortOrgId", None),
            orgProductToken=input_message.get("orgProductToken", None),
            uiHostUrl=input_message.get("uiHostUrl", None),
            jobId=input_message.get("jobId", None),
            stepId=input_message.get("stepId", None),
            versionId=input_message.get("versionId", None),
            nextStepId=input_message.get("nextStepId", None),
            nextEdgeId=input_message.get("nextEdgeId", None),
            triggerId=input_message.get("triggerId", None),
            jobExecutionContextId=input_message.get("jobExecutionContextId", None),
            time=input_message.get("time", None),
            connectionTestId=input_message.get("connectionTestId", None),
            connectionTestTimeout=input_message.get("connectionTestTimeout", None),
        )


class Meta(object):
    """ Meta properties for a plugin """

    def __init__(self, name="", vendor="", description="", version="", workflow=None):
        self.name, self.vendor, self.description, self.version, self.workflow = (
            name,
            vendor,
            description,
            version,
            workflow,
        )

    def set_workflow(self, input_message):
        """
        Sets the workflow attribute within the Meta class
        :param input_message:
        :return:
        """
        if input_message.get("workflow_uid"):
            self.workflow = Workflow.from_komand(input_message)
        else:
            self.workflow = Workflow.from_insight_connect(input_message)


class Plugin(object):
    """A Komand Plugin."""

    def __init__(
        self,
        name="",
        vendor="",
        description="",
        version="",
        connection=None,
        custom_encoder=None,
        custom_decoder=None,
    ):
        self.name = name
        self.vendor = vendor
        self.description = description
        self.version = version
        self.connection = connection

        self.connection.meta = Meta(
            name=name, vendor=vendor, description=description, version=version
        )

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
            "log": log,
            "status": "ok" if success else "error",
            "meta": input_message["body"].get("meta", None),
        }
        if success:
            output_message["output"] = output
        else:
            output_message["error"] = error_message
        return {"body": output_message, "version": "v1", "type": message_type}

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
            raise ClientException("input JSON was invalid", e)
        except Exception as e:
            raise Exception("Unable to validate input JSON", e)

    @staticmethod
    def validate_input_message(input_message):
        if input_message is None:
            raise ClientException("Input message was None")
        if not isinstance(input_message, dict):
            raise ClientException("Input message is not a dictionary")
        if "type" not in input_message:
            raise ClientException('"type" missing from input message')
        if "version" not in input_message:
            raise ClientException('"version" missing from input message')
        if "body" not in input_message:
            raise ClientException('"body" missing from input message')

        version = input_message["version"]
        type_ = input_message["type"]
        body = input_message["body"]

        if version != "v1":
            raise ClientException(
                "Unsupported version %s. Only v1 is supported".format(version)
            )
        if type_ == "action_start":
            if "action" not in body:
                raise ClientException(
                    'Message is action_start but field "action" is missing from body'
                )
            if not isinstance(body["action"], str):
                raise ClientException("Action field must be a string")
        elif type_ == "trigger_start":
            if "trigger" not in body:
                raise ClientException(
                    'Message is trigger_start but field "trigger" is missing from body'
                )
            if not isinstance(body["trigger"], str):
                raise ClientException("Trigger field must be a string")
        else:
            raise ClientException(
                "Unsupported message type %s. Must be action_start or trigger_start"
            )

        if "meta" not in body:
            body["meta"] = {}

        # This is existing behavior.
        if "connection" not in body:
            body["connection"] = {}
        if "dispatcher" not in body:
            body["dispatcher"] = {}
        if "input" not in body:
            body["input"] = {}

    def handle_step(self, input_message, is_test=False, is_debug=False):
        """
        Executes a single step, given the input message dictionary.

        Execution of this method is designed to be thread safe.

        :param input_message: The input message
        :param is_test: Whether or not this is
        :param is_debug:
        :return:
        """
        input_message_meta = input_message["body"].get("meta", {})

        if input_message_meta is None:
            input_message_meta = {}
        self.connection.meta.set_workflow(input_message_meta)
        request_id = uuid.uuid4()
        log_stream = io.StringIO()
        stream_handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("step_handler_{}".format(request_id))
        logger.setLevel("DEBUG" if is_debug else "INFO")
        logger.addHandler(stream_handler)

        success = True
        ex = None
        output = None
        out_type = None

        try:
            # Attempt to grab message type first
            message_type = input_message.get("type")
            out_type = message_output_type.get(message_type)
            if message_type not in ["action_start", "trigger_start"]:
                raise ClientException(
                    'Unsupported message type "{}"'.format(message_type)
                )

            Plugin.validate_input_message(input_message)

            if message_type == "action_start":
                out_type = "action_event"
                output = self.start_step(
                    input_message["body"],
                    "action",
                    logger,
                    log_stream,
                    is_test,
                    is_debug,
                )
            elif message_type == "trigger_start":
                out_type = "trigger_event"
                output = self.start_step(
                    input_message["body"],
                    "trigger",
                    logger,
                    log_stream,
                    is_test,
                    is_debug,
                )
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
            output = Plugin.envelope(
                out_type, input_message, log_stream.getvalue(), success, output, str(ex)
            )
            if not success:
                raise LoggedException(ex, output)
            return output

    def start_step(
        self, message_body, step_key, logger, log_stream, is_test=False, is_debug=False
    ):
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
        dictionary = getattr(self, step_key + "s")
        if action_name not in dictionary:
            raise ClientException('Unknown {} "{}"'.format(step_key, action_name))
        action = dictionary[action_name]

        connection = self.connection_cache.get(message_body["connection"], logger)

        # Copy the action for thread safety.
        # This is necessary because the object itself contains stateful fields like connection and debug.
        step = copy.copy(action)

        step.debug = is_debug
        step.connection = connection
        step.logger = logger

        # Extra setup for triggers
        if step_key == "trigger":
            step.log_stream = log_stream
            step.meta = message_body["meta"]
            step.webhook_url = message_body["dispatcher"]["webhook_url"]
            step.url = message_body["dispatcher"]["url"]

            if not step.dispatcher:
                if step.debug:
                    step.dispatcher = Stdout(message_body["dispatcher"])
                else:
                    step.dispatcher = Http(message_body["dispatcher"])

        params = message_body["input"]

        if not is_test:
            # Validate input message
            try:
                step.input.validate(params)

                # Validate required inputs
                # Step inputs will be checked against schema for required properties existence
                # This is needed to prevent null/empty string values from being passed as output to input of steps
                step.input.validate_required(params)
            except jsonschema.exceptions.ValidationError as e:
                raise ClientException("{} input JSON was invalid".format(step_key), e)
            except Exception as e:
                raise Exception("Unable to validate {} input JSON".format(step_key), e)

        # Log step information for improved debugging with users
        step.logger.info(
            "{vendor}/{plugin_name}:{plugin_version}. Step name: {step_name}".format(
                vendor=step.connection.meta.vendor,
                plugin_name=step.connection.meta.name,
                plugin_version=step.connection.meta.version,
                step_name=step.name,
            )
        )

        if is_test:
            # Check if connection test func available. If so - use it (preferred). Else fallback to action/trigger test
            if hasattr(step.connection, "test"):
                func = step.connection.test
            else:
                func = step.test
        else:
            func = step.run

        # Backward compatibility with steps with missing argument params
        # The SDK has always defined the signature of the run/test methods to include the params dictionary.
        # However, the code generation generates the test method without the params argument.
        parameters = inspect.signature(func)
        if len(parameters.parameters) > 0:
            output = func(params)
        else:
            output = func()

        # Don't validate output for any test functions - action/trigger tests shouldn't be validated due to them
        # not providing value and a connection test shouldn't be validated due to it being generic/universal
        if not is_test:
            step.output.validate(output)

        return output
