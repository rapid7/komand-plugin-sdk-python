# -*- coding: utf-8 -*-
from jsonschema import validate

import komand.util as util


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
