import komand
from .schema import SayGoodbyeInput, SayGoodbyeOutput, Input, Output, Component
# Custom imports below


class SayGoodbye(komand.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
                name='say_goodbye',
                description=Component.DESCRIPTION,
                input=SayGoodbyeInput(),
                output=SayGoodbyeOutput())

    def run(self, params={}):
        # TODO: Implement run function
        return {}
