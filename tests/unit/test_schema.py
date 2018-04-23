import json
import jsonschema

input_message_schema = json.load(open('./komand/data/input_message_schema.json'))
output_message_schema = json.load(open('./komand/data/output_message_schema.json'))


def test_json_schema_1():
    j = {
        'version': 'v1',
        'type': 'action_start',
        'body': {
            'meta': None,
            'action': 'hello',
            'trigger': '',
            'connection': {
                'greeting': 'Hello, {}!'
            },
            'dispatcher': None,
            'input': {
                'name': 'wow'
            }
        }
    }
    jsonschema.validate(j, input_message_schema)
