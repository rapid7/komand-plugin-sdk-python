from jsonschema import validate
import komand.util as util
import komand.helper as helper


class Connection(object):
    """Komand connection"""
    def __init__(self, input):
        # Maintain backwards compatibility here - if Input object passed in it will have a 'schema' property so use that
        # Otherwise, the input is a JSON schema, so just use it directly
        if hasattr(input, "schema"):
            self.schema = input.schema
        else:
            self.schema = input
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
