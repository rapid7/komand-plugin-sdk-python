# -*- coding: utf-8 -*-
import sys
import json
import io
import six
from plugin import plugin
from komand.cli import CLI

cli = CLI(plugin)


class Python2StringIO(io.StringIO):
    def write(self, s):
        if isinstance(s, str):
            s = s.decode('utf-8')
        super(Python2StringIO, self).write(s)


def capture_stdout():
    old = sys.stdout
    if six.PY2:
        sys.stdout = Python2StringIO()
    else:
        sys.stdout = io.StringIO()

    cli.run()

    value = sys.stdout.getvalue()
    sys.stdout = old

    return value


def test_cli_info():
    cli.args = ['info']
    actual_value = capture_stdout()
    expected_value = u"""Name:        [92mHelloWorld[0m
Vendor:      [92mkomand[0m
Version:     [92m1.0.0[0m
Description: [92mHello World plugin[0m

Triggers ([92m1[0m):
└── [92mtrigger[0m (description[0m)

Actions ([92m1[0m):
└── [92maction[0m (description[0m)

"""
    assert actual_value == expected_value


def test_cli_sample_action():
    cli.args = ['sample', 'action']
    value = capture_stdout()
    expected_value = u'{"body": {"action": "action", "meta": {}, "input": {"name": ""}, ' + \
                     '"connection": {"greeting": ""}}, "type": "action_start", "version": "v1"}'
    assert json.loads(value) == json.loads(expected_value)


def test_cli_sample_trigger():
    cli.args = ['sample', 'trigger']
    value = capture_stdout()
    expected_value = u'{"body": {"trigger": "trigger", "meta": {}, "input": {"name": ""}, ' + \
                     '"dispatcher": {"url": "http://localhost:8000", "webhook_url": ""}, ' + \
                     '"connection": {"greeting": ""}}, "type": "trigger_start", "version": "v1"}'
    assert json.loads(value) == json.loads(expected_value)


def test_cli_test_action():
    cli.args = ['test']
    sys.stdin = open('./tests/plugin/action/input.json')
    expected_output = json.load(open('./tests/plugin/action/test_output.json'))
    actual_output = json.loads(capture_stdout())
    assert actual_output == expected_output


def test_cli_test_trigger():
    cli.args = ['test']
    sys.stdin = open('./tests/plugin/trigger/input.json')
    expected_output = json.load(open('./tests/plugin/trigger/test_output.json'))
    actual_output = json.loads(capture_stdout())
    assert actual_output == expected_output


def test_cli_run_action():
    cli.args = ['run']
    sys.stdin = open('./tests/plugin/action/input.json')
    expected_output = json.load(open('./tests/plugin/action/output.json'))
    actual_output = json.loads(capture_stdout())
    assert actual_output == expected_output
