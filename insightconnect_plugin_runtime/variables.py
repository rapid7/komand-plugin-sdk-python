# -*- coding: utf-8 -*-
from jsonschema import validate
import insightconnect_plugin_runtime.util as util
from insightconnect_plugin_runtime.exceptions import ClientException


class Input(object):
    """ Input variables """

    def __init__(self, schema):
        self.schema = schema
        self.parameters = None

    def set(self, parameters, should_validate=True):
        """ Set parameters """
        self.parameters = parameters
        if should_validate:
            self.validate(self.parameters)

    def validate(self, parameters):
        """ Validate variables """
        validate(parameters, self.schema)

    def validate_required(self, parameters):
        """
        Validates required input parameters for invalid values (null, empty string) and raises an Exception in their
        presence.
        In the future, this should probably be built into an existing JSONSchema validator
        :param parameters: Input parameters
        :return: None
        """
        required = "required"
        message = (
            "Step error: Plugin step input contained a null value or empty string in a required input.\n"
            "If the input was given a variable in the Workflow Builder, please double-check that the variable "
            "contained a value at run-time. If the input had a valid value and the issue persists, "
            "please contact support for assistance.\nInvalid input was found in: {key}"
        )

        # Early return if there's nothing for this function to do
        if required not in self.schema:
            return

        required_inputs = self.schema[
            required
        ]  # List of required inputs, pulled from the jsonschema

        # Iterate over parameters (inputs, k:v pairs) with the key to check for presence in the list
        # of required inputs from above. If present, check the value is "valid" according to our guidelines
        # (no null values, no empty strings). Note that the InsightConnect UI seems to mutate null values
        # into empty strings. Retain the null check as it is possible this behavior changes in future iterations.
        for key in parameters:
            if key in required_inputs:
                value = parameters[key]

                # Check if the value is null OR the value is a string and has a length of 0
                # Logic is expanded due to the fact that we don't want to false-positive on False boolean values
                if (value is None) or (isinstance(value, str) and not len(value)):
                    raise ClientException(message.format(key=key))

    def sample(self):
        """ Sample object """
        return util.sample(self.schema)


class Output(object):
    """ Output variables """

    def __init__(self, schema):
        self.schema = schema
        self.parameters = None

    def set(self, parameters, should_validate=True):
        """ Set parameters """
        self.parameters = parameters
        if should_validate:
            self.validate(self.parameters)

    def validate(self, parameters):
        """ Validate variables """
        validate(parameters, self.schema)

    def sample(self):
        """ Sample object """
        return util.sample(self.schema)
