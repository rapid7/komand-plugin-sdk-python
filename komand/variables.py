# -*- coding: utf-8 -*-
from jsonschema import validate
import komand.util as util
import logging


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
        :param parameters: Input parameters
        :return: None
        """
        logging.info("VALIDATING REQUIRED FIELDS!!!")
        required_inputs = self.schema["required"]

        for key in parameters:
            if key in required_inputs:
                if parameters[key] is None:  # Check for null
                    raise Exception("Step error: Plugin step contained a null value in a required input.\n"
                                    "Please contact support for assistance.\n"
                                    "Missing input was: %s" % key)
                elif isinstance(parameters[key], str) and not parameters[key]:  # Check for 0-length strings
                    raise Exception("Step error: Plugin step contained an empty string in a required input.\n"
                                    "Please contact support for assistance.\n"
                                    "Empty string input was: %s" % key)

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
