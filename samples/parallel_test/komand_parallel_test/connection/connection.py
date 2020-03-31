import insightconnect_plugin_runtime
import logging
from .schema import ConnectionSchema
import os
import threading

# Custom imports below


class Connection(insightconnect_plugin_runtime.Connection):
    def __init__(self):
        super(self.__class__, self).__init__(input=ConnectionSchema())

    def connect(self, params={}):
        logging.info(
            "Connection made from Proc {} Thread {}".format(
                os.getpid(), threading.current_thread()._name
            )
        )
