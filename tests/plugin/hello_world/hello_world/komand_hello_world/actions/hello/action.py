import insightconnect_plugin_runtime
from .schema import HelloInput, HelloOutput

# Custom imports below


class Hello(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="hello",
            description="Print hello world",
            input=HelloInput(),
            output=HelloOutput(),
        )

    def run(self, params={}):
        self.logger.info("I am the log")
        return {"message": self.connection.greeting.format(params["name"])}

    def test(self, params={}):
        self.logger.info("This is a test")
        return {"message": "Test greeting"}
