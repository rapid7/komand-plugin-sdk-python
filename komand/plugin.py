# -*- coding: utf-8 -*-
import komand.server
from .connection import ConnectionCache


class Plugin(object):
    """A Komand Plugin."""

    def __init__(self, name='', vendor='', description='', version='', connection=None, custom_encoder=None,
                 custom_decoder=None):
        self.name = name
        self.vendor = vendor
        self.description = description
        self.version = version
        self.connection = connection
        self.connection_cache = ConnectionCache(connection)
        self.triggers = {}
        self.actions = {}
        self.debug = False
        self.custom_decoder = custom_decoder
        self.custom_encoder = custom_encoder

    def server(self, port=8001):
        server = komand.server.PluginServer(
            plugin=self,
            port=port,
            debug=self.debug,
            )

        server.start()

    def add_trigger(self, trigger):
        """ add a new trigger """
        self.triggers[trigger.name] = trigger

    def add_action(self, action):
        """ add a new action """
        self.actions[action.name] = action
