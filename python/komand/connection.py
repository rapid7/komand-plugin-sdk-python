from jsonschema import validate


class Connection(object):
    """Komand connection"""
    def __init__(self, schema={}):
        self.schema = schema 
        self.parameters = {}

    def set(self, parameters):
        """ Set parameters """
        self.parameters = parameters
        self._validate()

    def _validate(self):
        """ Validate variables """
        validate(self.parameters, self.schema)

    def connect(self):
        """ Connect """
        raise NotImplementedError
