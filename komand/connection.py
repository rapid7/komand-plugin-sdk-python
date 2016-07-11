from jsonschema import validate
import util

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
        if self.schema:
            validate(self.parameters, self.schema)

    def connect(self, params={}):
        """ Connect """
        raise NotImplementedError

    def sample(self):
        """ Sample object """
        if self.schema:
            return util.sample(self.schema)
    

