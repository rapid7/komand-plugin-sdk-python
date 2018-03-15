import komand
import time
from .schema import EmitGreetingInput, EmitGreetingOutput
import logging
# Custom imports below


class EmitGreeting(komand.Trigger):

    def __init__(self):
        super(self.__class__, self).__init__(
            name='emit_greeting',
            description='emit greeting',
            input=EmitGreetingInput(),
            output=EmitGreetingOutput())

    def run(self):
        logging.info("RUNNING TRIGGER", self.input, self.output)
        while True:
            self.send({'greeting': 'howdy', 'name': 'friend'})
            time.sleep(5)

    def test(self):
        logging.info("TESTING TRIGGER", self.input.parameters)
        return {
            'greeting': 'hello', 'name': self.input.parameters['face']
        }
