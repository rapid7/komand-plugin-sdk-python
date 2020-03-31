import insightconnect_plugin_runtime
import time
from .schema import ReturnBadJsonTriggerInput, ReturnBadJsonTriggerOutput

# Custom imports below


class ReturnBadJsonTrigger(insightconnect_plugin_runtime.Trigger):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="return_bad_json_trigger",
            description="This trigger will return JSON which doesnt match the spec",
            input=ReturnBadJsonTriggerInput(),
            output=ReturnBadJsonTriggerOutput(),
        )

    def run(self, params={}):
        """Run the trigger"""
        while True:
            self.send({})
            time.sleep(params.get("interval", 5))

    def test(self):
        return {}
