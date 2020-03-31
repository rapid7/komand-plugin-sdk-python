import insightconnect_plugin_runtime
import time
from .schema import HelloTriggerInput, HelloTriggerOutput

# Custom imports below


class HelloTrigger(insightconnect_plugin_runtime.Trigger):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="hello_trigger",
            description="Prints a greeting every 10 seconds",
            input=HelloTriggerInput(),
            output=HelloTriggerOutput(),
        )

    def run(self, params={}):
        """Run the trigger"""
        while True:
            self.logger.info("I am the log")
            self.send({"message": self.connection.greeting.format(params["name"])})
            time.sleep(10)

    def test(self):
        self.logger.info("This is a test")
        return {"message": "Test greeting"}
