from .komand_hello_world.connection import Connection
from .komand_hello_world.actions import Hello, ReturnBadJson, ThrowException
from .komand_hello_world.triggers import HelloTrigger
from .komand_hello_world.triggers import ReturnBadJsonTrigger
from .komand_hello_world.triggers import ThrowExceptionTrigger

import insightconnect_plugin_runtime


Name = "Hello_world"
Vendor = "komand"
Version = "1.0.0"
Description = "A hello world plugin for SDK testing"


class KomandHelloWorld(insightconnect_plugin_runtime.Plugin):
    def __init__(self):
        super(self.__class__, self).__init__(
            name=Name,
            vendor=Vendor,
            version=Version,
            description=Description,
            connection=Connection(),
        )
        self.add_trigger(HelloTrigger())

        self.add_trigger(ReturnBadJsonTrigger())

        self.add_trigger(ThrowExceptionTrigger())

        self.add_action(Hello())

        self.add_action(ReturnBadJson())

        self.add_action(ThrowException())
