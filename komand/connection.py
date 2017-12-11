class Connection(object):
    """Komand connection"""

    def __init__(self, input):
        self.schema = input.schema
        self.parameters = {}

    def connect(self, params={}):
        """ Connect """
        raise NotImplementedError
