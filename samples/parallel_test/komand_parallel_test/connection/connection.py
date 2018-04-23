import komand
import logging
from .schema import ConnectionSchema
import os
import threading
# Custom imports below


class Connection(komand.Connection):

    def __init__(self):
        super(self.__class__, self).__init__(input=ConnectionSchema())

    def connect(self, params={}):
        logging.info('Connection made from Proc {} Thread {}'.format(os.getpid(), threading.current_thread()._name))
