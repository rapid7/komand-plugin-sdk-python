# -*- coding: utf-8 -*-
from jsonschema import validate
import komand.util as util
import logging
from komand.exceptions import ClientException
from six import string_types  # Needed for Py2/3 string-type validation


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

        # Early return if there's nothing for this function to do
        if required not in self.schema:
            return

        required_inputs = self.schema[required]

        for key in parameters:
            if key in required_inputs:
                value = parameters[key]

                if value is None:  # Check for null
                    raise ClientException("Step error: Plugin step contained a null value in a required input.\n"
                                          "Please contact support for assistance.\n"
                                          "Missing input was: %s" % key)
                elif isinstance(value, string_types) and not len(value):  # Check for 0-length strings
                    raise ClientException("Step error: Plugin step contained an empty string in a required input.\n"
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
