# GENERATED BY KOMAND SDK - DO NOT EDIT
import komand
import json


class ConnectionSchema(komand.Input):
    schema = json.loads("""
   {}
    """)

    def __init__(self):
        super(self.__class__, self).__init__(self.schema)
