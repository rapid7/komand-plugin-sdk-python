import insightconnect_plugin_runtime
from .schema import RespondInput, RespondOutput
import logging

# Custom imports below


class Respond(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="respond",
            description="respond to something",
            input=RespondInput(),
            output=RespondOutput(),
        )

    def run(self):
        logging.info("RUNNING ACTION", self.input, self.output)
        return self.input.parameters

    def test(self):
        logging.info("TESTING ACTION", self.input, self.output)
        return self.output.validate({"hello": "there"})
