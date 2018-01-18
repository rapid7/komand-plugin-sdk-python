from jsonschema import validate
import komand.util as util
import komand.helper as helper
import json
import hashlib
import copy

def key(parameters):
   """key is a unique connection key"""
   return hashlib.sha1(json.dumps(parameters, sort_keys=True).encode('utf-8')).hexdigest()

class ConnectionCache(object):
    def __init__(self, prototype):
        self.connections = {}
        self.prototype = prototype

    def get(self, parameters):
        conn_key = key(parameters)

        # we could 'lock' this data  structure
        # but honestly i  don't see the point
        # worst case in a race condition is that
        # we create 2 copies of the connection, and
        # the later one overrides the first one.
        #
        # for real connection pooling we will need to fix this.
        if conn_key in self.connections:
            return self.connections[conn_key]

        conn = copy.copy(self.prototype)
        conn.set(parameters)
        # i don't know why this is needed twice..
        # i think for backwards compat reasons
        conn.connect(parameters)
        self.connections[conn.key()] = conn
        return conn



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

    def key(self):
        """key is a unique connection key"""
        return key(self.parameters)

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
