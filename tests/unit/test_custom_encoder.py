import json
import decimal

from insightconnect_plugin_runtime.action import Action
from insightconnect_plugin_runtime.variables import Input, Output
from insightconnect_plugin_runtime.connection import Connection


def test_custom_encoder_action_succeeds():
    class DecimalEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, decimal.Decimal):
                if o % 1 > 0:
                    # This is potentially dangerous - it seems simplejson treats these as strings
                    return float(o)
                else:
                    return int(o)
            return super(DecimalEncoder, self).default(o)

    class CustomEncoderConnection(Connection):
        schema = {
            "type": "object",
            "properties": {"price": {"type": "number"}, "name": {"type": "string"},},
        }

        def __init__(self):
            super(self.__class__, self).__init__(self.schema)

        def connect(self, params={}):
            return None

    class CustomEncoderActionInput(Input):
        schema = {"type": "object", "properties": {"greeting": {"type": "string"},}}

        def __init__(self):
            super(self.__class__, self).__init__(schema=self.schema)

    class CustomEncoderActionOutput(Output):
        schema = {
            "type": "object",
            "required": ["price", "name"],
            "properties": {"price": {"type": "number"}, "name": {"type": "string"},},
        }

        def __init__(self):
            super(self.__class__, self).__init__(schema=self.schema)

    class CustomEncoderAction(Action):
        def __init__(self):
            super(self.__class__, self).__init__(
                "stupid",
                "an action",
                CustomEncoderActionInput(),
                CustomEncoderActionOutput(),
            )

        def run(self, params={}):
            return {"price": decimal.Decimal("1100.0"), "name": "Jon"}

        def test(self, params={}):
            return {"price": decimal.Decimal("1.1"), "name": "Jon"}
