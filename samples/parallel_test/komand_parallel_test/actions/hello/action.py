import insightconnect_plugin_runtime
from .schema import HelloInput, HelloOutput
import os
import threading

# Custom imports below


class Hello(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="hello",
            description="Print information",
            input=HelloInput(),
            output=HelloOutput(),
        )
        self.count = 0

    def run(self, params={}):
        message = "Hello {} from Proc {} Thread {}".format(
            self.count, os.getpid(), threading.current_thread()._name
        )
        self.count = self.count + 1
        return {"message": message}

    def test(self, params={}):
        return self.run(params)
