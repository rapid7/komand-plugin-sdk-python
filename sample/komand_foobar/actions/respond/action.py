import komand
from .schema import RespondInput, RespondOutput
import logging
# Custom imports below


class Respond(komand.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name='respond',
            description='respond to something',
            input=RespondInput(),
            output=RespondOutput())

    def run(self):
        logging.info("RUNNING ACTION", self.input, self.output)
        return self.input.parameters

    def test(self):
        logging.info("TESTING ACTION", self.input, self.output)
        return self.output.validate({'hello': 'there'})
