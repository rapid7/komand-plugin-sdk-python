# GENERATED BY KOMAND SDK - DO NOT EDIT
import insightconnect_plugin_runtime
import json


class Component:
    DESCRIPTION = "Emit say goodbye message"


class Input:
    NAME = "name"
    

class Output:
    MESSAGE = "message"
    

class SayGoodbyeInput(insightconnect_plugin_runtime.Input):
    schema = json.loads("""
   {
  "type": "object",
  "title": "Variables",
  "properties": {
    "name": {
      "type": "string",
      "title": "Name",
      "description": "Name to say goodbye to",
      "order": 1
    }
  },
  "required": [
    "name"
  ]
}
    """)

    def __init__(self):
        super(self.__class__, self).__init__(self.schema)


class SayGoodbyeOutput(insightconnect_plugin_runtime.Output):
    schema = json.loads("""
   {
  "type": "object",
  "title": "Variables",
  "properties": {
    "message": {
      "type": "string",
      "title": "Message",
      "order": 1
    }
  },
  "required": [
    "message"
  ]
}
    """)

    def __init__(self):
        super(self.__class__, self).__init__(self.schema)
