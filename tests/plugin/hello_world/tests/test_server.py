# -*- coding: utf-8 -*-
from flask import json


def run_action(client, input_file, output_file, expect_code=200, is_test=False):
    """
    Helper to run action with flask client
    """

    input_message = json.load(open(input_file))
    expected_output = json.load(open(output_file))

    headers = {"Content-type": "application/json", "Accept": "text/plain"}

    url = f"/actions/{input_message['body']['action']}"
    if is_test:
        url = f"{url}/test"

    response = client.post(url, json=input_message, headers=headers)
    assert response.status_code == expect_code

    output = json.loads(response.data)

    if "body" in output and "log" in output["body"]:
        output["body"]["log"] = ""

    if "body" in expected_output and "log" in expected_output["body"]:
        expected_output["body"]["log"] = ""

    if output != expected_output:
        raise Exception(
            f"Actual output differs from expected output.{output} != {expected_output}"
        )


def test_404(plugin_server):
    """
    GIVEN a Flask application
    WHEN the '/' page is requested (GET)
    THEN check the response is valid
    """
    response = plugin_server.post("/")
    assert response.status_code == 404


def test_server_simple_action(plugin_server):
    run_action(
        plugin_server,
        "./tests/plugin/hello_world/tests/action/hello/input.json",
        "./tests/plugin/hello_world/tests/action/hello/output.json",
    )


def test_server_bad_action(plugin_server):
    run_action(
        plugin_server,
        "./tests/plugin/hello_world/tests/action/throw_exception/input.json",
        "./tests/plugin/hello_world/tests/action/throw_exception/output.json",
        expect_code=500,
    )


def test_server_bad_json_action(plugin_server):
    run_action(
        plugin_server,
        "./tests/plugin/hello_world/tests/action/return_bad_json/input.json",
        "./tests/plugin/hello_world/tests/action/return_bad_json/output.json",
        expect_code=500,
    )


def test_server_test_simple_action(plugin_server):
    run_action(
        plugin_server,
        "./tests/plugin/hello_world/tests/action/hello/input.json",
        "./tests/plugin/hello_world/tests/action/hello/test_output.json",
        expect_code=200,
        is_test=True,
    )


def test_server_test_throw_exeception_action(plugin_server):
    run_action(
        plugin_server,
        "./tests/plugin/hello_world/tests/action/throw_exception/input.json",
        "./tests/plugin/hello_world/tests/action/throw_exception/test_output.json",
        expect_code=500,
        is_test=True,
    )


def test_server_api_spec(plugin_server):
    api_spec = plugin_server.get("/api/v1/api")
    assert api_spec.status_code == 200

    api_spec_json = json.loads(api_spec.data)

    assert api_spec_json["info"]["title"] == "InsightConnect Plugin Runtime API"


def test_server_api_status(plugin_server):
    response = plugin_server.get("/api/v1/status")
    assert response.status_code == 200

    response_json = json.loads(response.data)

    assert response_json["status"] == "Ready"


def test_server_api_actions(plugin_server):
    response = plugin_server.get("/api/v1/actions")
    assert response.status_code == 200

    response_json = json.loads(response.data)
    expected = ["hello", "return_bad_json", "throw_exception"]

    assert sorted(expected) == sorted(response_json)


def test_server_api_triggers(plugin_server):
    response = plugin_server.get("/api/v1/triggers")
    assert response.status_code == 200

    response_json = json.loads(response.data)
    expected = ["hello_trigger", "return_bad_json_trigger", "throw_exception_trigger"]

    assert sorted(expected) == sorted(response_json)
