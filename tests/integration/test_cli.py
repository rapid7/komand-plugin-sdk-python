import sys
import json
import io

from tests.integration.plugin import plugin
from komand.cli import CLI

cli = CLI(plugin)


def capture_stdout():
    old = sys.stdout
    sys.stdout = io.StringIO()

    cli.run()

    value = sys.stdout.getvalue()
    sys.stdout = old

    return value


def test_cli_info():
    cli.args = ['info']
    value = capture_stdout()
    assert value == """Name:        [92mHelloWorld[0m
Vendor:      [92mkomand[0m
Version:     [92m1.0.0[0m
Description: [92mHello World plugin[0m

Triggers ([92m1[0m): 
└── [92mtrigger[0m (description[0m)

Actions ([92m1[0m): 
└── [92maction[0m (description[0m)

"""


def test_cli_sample_action():
    cli.args = ['sample', 'action']
    value = capture_stdout()
    assert value == '{"body": {"action": "action", "meta": {}, "input": {"name": ""}, "connection": {"greeting": ""}}, "type": "action_start", "version": "v1"}'


def test_cli_sample_trigger():
    cli.args = ['sample', 'trigger']
    value = capture_stdout()
    assert value == '{"body": {"trigger": "trigger", "meta": {}, "input": {"name": ""}, "dispatcher": {"url": "http://localhost:8000", "webhook_url": ""}, "connection": {"greeting": ""}}, "type": "trigger_start", "version": "v1"}'


def test_cli_test_action():
    cli.args = ['test']
    sys.stdin = open('./tests/integration/action/input.json')
    expected_output = json.load(open('./tests/integration/action/test_output.json'))
    actual_output = json.loads(capture_stdout())
    assert actual_output == expected_output


def test_cli_test_trigger():
    cli.args = ['test']
    sys.stdin = open('./tests/integration/trigger/input.json')
    expected_output = json.load(open('./tests/integration/trigger/test_output.json'))
    actual_output = json.loads(capture_stdout())
    assert actual_output == expected_output


def test_cli_run_action():
    cli.args = ['run']
    sys.stdin = open('./tests/integration/action/input.json')
    expected_output = json.load(open('./tests/integration/action/output.json'))
    actual_output = json.loads(capture_stdout())
    assert actual_output == expected_output


def test_cli_run_trigger():
    cli.args = ['run']
    sys.stdin = open('./tests/integration/trigger/input.json')
    expected_output = json.load(open('./tests/integration/action/output.json'))
    actual_output = json.loads(capture_stdout())
    assert actual_output == expected_output
