import komand
import logging

class RespondInput(komand.Input):
    schema = {
       "type" : "object",
       "properties": {
           "foo": {
               "type": "string"
               },
           "bar": {
               "type": "string"
               },
           },
       }

    def __init__(self):
        super(self.__class__, self).__init__(self.schema)
       

class RespondOutput(komand.Output):
    schema = {
       "type" : "object",
       "properties": {
           "foo": {
               "type": "string"
               },
           "bar": {
               "type": "string"
               },
           },
       }

    def __init__(self):
        super(self.__class__, self).__init__(self.schema)


class Respond(komand.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
                name='respond',
                description='respond to something',
                input=RespondInput(), 
                output=RespondOutput())

    def run(self):
        logging.info("RUNNING ACTION", self.input, self.output)
            

    def test(self):
        logging.info("TESTING ACTION", self.input, self.output)
        return self.output.validate({ 'hello': 'there' })

