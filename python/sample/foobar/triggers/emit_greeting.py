import komand
import logging

class EmitGreetingInput(komand.Input):
    schema = {
       "type" : "object",
       "properties": {
           "face": {
               "type": "string"
               },
           },
       }

    def __init__(self):
        super(self.__class__, self).__init__(self.schema)
       

class EmitGreetingOutput(komand.Output):
    schema = {
       "type" : "object",
       "properties": {
           "greeting": {
               "type": "string"
               },
           "name": {
               "type": "string"
               },
           },
       }

    def __init__(self):
        super(self.__class__, self).__init__(self.schema)


class EmitGreeting(komand.Trigger):

    def __init__(self):
        super(self.__class__, self).__init__(
                name='emit_greeting',
                description='emit greeting',
                input=EmitGreetingInput(), 
                output=EmitGreetingOutput())

    def run(self):
        logging.info("RUNNING TRIGGER", self.input, self.output)
            

    def test(self):
        logging.info("TESTING TRIGGER", self.input.parameters)
        return { 'greeting': 'hello', 'name': self.input.parameters['face'] }

