import insightconnect_plugin_runtime
import logging
from .schema import ConnectionSchema

# Custom imports below


class Connection(insightconnect_plugin_runtime.Connection):
    def __init__(self):
        super(self.__class__, self).__init__(input=ConnectionSchema())

        self.greeting = None

    def connect(self, params):
        self.greeting = params["greeting"]
