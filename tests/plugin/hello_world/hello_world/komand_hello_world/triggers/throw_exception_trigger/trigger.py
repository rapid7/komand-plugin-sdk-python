import insightconnect_plugin_runtime
import time
from .schema import ThrowExceptionTriggerInput, ThrowExceptionTriggerOutput

# Custom imports below


class ThrowExceptionTrigger(insightconnect_plugin_runtime.Trigger):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="throw_exception_trigger",
            description="This trigger will always throw an exception as soon as its invoked",
            input=ThrowExceptionTriggerInput(),
            output=ThrowExceptionTriggerOutput(),
        )

    def run(self, params={}):
        raise Exception("because I can")

    def test(self, params={}):
        raise Exception("because I can")
