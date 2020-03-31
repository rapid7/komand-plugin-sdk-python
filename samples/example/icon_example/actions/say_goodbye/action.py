import insightconnect_plugin_runtime
from .schema import SayGoodbyeInput, SayGoodbyeOutput, Input, Output, Component

# Custom imports below


class SayGoodbye(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="say_goodbye",
            description=Component.DESCRIPTION,
            input=SayGoodbyeInput(),
            output=SayGoodbyeOutput(),
        )

    def run(self, params={}):
        return {Output.MESSAGE: f"Goodbye, {params.get(Input.NAME)}"}
