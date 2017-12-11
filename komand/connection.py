from jsonschema import validate
import komand.util as util
import komand.helper as helper


class Connection(object):
    """Komand connection"""

    def __init__(self, input):
        self.schema = input.schema
        self.parameters = {}

    def connect(self, params={}):
        """ Connect """
        raise NotImplementedError

    def set(self, parameters):
        """ Set parameters """
        self.parameters = parameters
        self._validate()

    def _validate(self):
        """ Validate variables """
        if self.schema:
            validate(self.parameters, self.schema)

    def sample(self):
        """ Sample object """
        if self.schema:
            return util.sample(self.schema)
