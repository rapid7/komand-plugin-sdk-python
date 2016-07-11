import komand
import logging

class Connection(komand.Connection):
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
        
    def connect(self):
        """ No-op"""
        logging.info("connecting")





