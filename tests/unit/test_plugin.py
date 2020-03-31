from insightconnect_plugin_runtime.plugin import Plugin
import json
import jsonschema

input_message_schema = json.load(
    open("./insightconnect_plugin_runtime/data/input_message_schema.json")
)


def code_agrees(input_message):
    plugin_success = True
    jsonschema_success = True
    try:
        Plugin.validate_input_message(input_message)
    except Exception as e:
        plugin_success = False
    try:
        jsonschema.validate(input_message, input_message_schema)
    except Exception as e:
        jsonschema_success = False
    assert plugin_success == jsonschema_success


def test_schema_matches_1():
    code_agrees(
        {
            "version": "v1",
            "type": "action_start",
            "body": {
                "meta": None,
                "action": "hello",
                "trigger": "",
                "connection": {"greeting": "Hello, {}!"},
                "dispatcher": None,
                "input": {"name": "wow"},
            },
        }
    )


def test_schema_matches_2():
    code_agrees(
        {
            "version": "v1",
            "type": "bad",
            "body": {
                "meta": None,
                "action": "hello",
                "trigger": "",
                "connection": {"greeting": "Hello, {}!"},
                "dispatcher": None,
                "input": {"name": "wow"},
            },
        }
    )


def test_schema_matches_3():
    code_agrees(
        {
            "version": "v2",
            "type": "action_start",
            "body": {
                "meta": None,
                "action": "hello",
                "trigger": "",
                "connection": {"greeting": "Hello, {}!"},
                "dispatcher": None,
                "input": {"name": "wow"},
            },
        }
    )


def test_schema_matches_4():
    code_agrees(
        {
            "version": "v1",
            "type": "action_start",
            "body": {
                "meta": None,
                "action": "hello",
                "trigger": "",
                "connection": {"greeting": "Hello, {}!"},
                "dispatcher": None,
                "input": None,
            },
        }
    )
