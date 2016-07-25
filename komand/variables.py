from jsonschema import validate
import util


class Input(object):
    """ Input variables """
    def __init__(self, schema):
        self.schema = schema

    def set(self, parameters, validate=True):
        """ Set parameters """
        self.parameters = parameters
        if validate:
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

    def set(self, parameters, validate=True):
        """ Set parameters """
        self.parameters = parameters
        if validate:
            self.validate(self.parameters)

    def validate(self, parameters):
        """ Validate variables """
        validate(parameters, self.schema)

    def sample(self):
        """ Sample object """
        return util.sample(self.schema)
    
