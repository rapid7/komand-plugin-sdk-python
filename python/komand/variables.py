from jsonschema import validate

class Input(object):
    """ Input variables """
    def __init__(self, schema):
        self.schema = schema

    def validate(self, parameters):
        validate(parameters, self.schema)
        return parameters

class Output(object):
    """ Output variables """
    def __init__(self, schema={}):
        self.schema = schema

    def validate(self, parameters):
        validate(parameters, self.schema)
        return parameters
