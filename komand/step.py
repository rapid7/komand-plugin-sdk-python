# -*- coding: utf-8 -*-
import logging

from io import StringIO


class Step(object):
    """A action"""

    def __init__(self, name, description, input, output):
        self.name = name
        self.description = description
        self.input = input
        self.output = output
        self.connection = None
        self.debug = False
        self.stream = StringIO()
        self.handler = logging.StreamHandler(self.stream)
        self.logger = logging.getLogger(self.name)

        self.logger.info("{vendor}-{plugin_name}-{plugin_version}:{step_name}".
                         format(vendor=self.connection.meta.vendor,
                                plugin_name=self.connection.meta.name,
                                plugin_version=self.connection.meta.version,
                                step_name=self.name))

    def run(self, params={}):
        """ Run a action, return output or raise error """
        raise NotImplementedError

    def test(self, params={}):
        """
        Test an action, return output or raise error
        Deprecated in favor of using the test function in the plugin connection.py file
        """
        pass
