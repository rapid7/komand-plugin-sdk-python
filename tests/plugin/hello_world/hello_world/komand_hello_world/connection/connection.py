import komand
import logging
from .schema import ConnectionSchema
# Custom imports below


class Connection(komand.Connection):

    def __init__(self):
        super(self.__class__, self).__init__(input=ConnectionSchema())

        self.greeting = None

    def connect(self, params):
        self.greeting = params['greeting']
