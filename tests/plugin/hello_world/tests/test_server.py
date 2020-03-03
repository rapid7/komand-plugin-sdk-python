# -*- coding: utf-8 -*-
from tests.plugin.hello_world import KomandHelloWorld
from komand import CLI
import pytest
import os
import requests
import time
import json

cli_pid = None


@pytest.fixture(scope="module")
def plugin_pid():

    if cli_pid:
        yield cli_pid
    else:
        cli = CLI(KomandHelloWorld())
        cli.args = ['http']

        pid = os.fork()
        if pid == 0:
            cli.run()
        else:
            for i in range(0, 10000):
                try:
                    requests.post('http://localhost:10001')
                    yield pid
                    os.kill(pid, 9)
                    break
                except Exception as e:
                    pass
    # Give the service time to start for testing purposes
    time.sleep(5)


def test_404(plugin_pid):
    assert requests.post('http://localhost:10001').status_code == 404


def run_action(input_file, output_file, expect_code=200, is_test=False):

    input_message = json.load(open(input_file))
    expected_output = json.load(open(output_file))

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    if is_test:
        url = 'http://localhost:10001/{}/{}/test'.format('actions', input_message['body']['action'])
    else:
        url = 'http://localhost:10001/{}/{}'.format('actions', input_message['body']['action'])

    response = requests.post(url, json=input_message, headers=headers)
    assert response.status_code == expect_code

    output = response.json()

    if 'body' in output and 'log' in output['body']:
        output['body']['log'] = ''

    if 'body' in expected_output and 'log' in expected_output['body']:
        expected_output['body']['log'] = ''

    if output != expected_output:
        raise Exception('Actual output differs from expected output.{} != {}'.format(output, expected_output))


def test_server_simple_action():
    run_action('./tests/plugin/hello_world/tests/action/hello/input.json',
               './tests/plugin/hello_world/tests/action/hello/output.json')


def test_server_bad_action():
    run_action('./tests/plugin/hello_world/tests/action/throw_exception/input.json',
               './tests/plugin/hello_world/tests/action/throw_exception/output.json', expect_code=500)


def test_server_bad_json_action():
    run_action('./tests/plugin/hello_world/tests/action/return_bad_json/input.json',
               './tests/plugin/hello_world/tests/action/return_bad_json/output.json', expect_code=500)


def test_server_test_simple_action():
    run_action('./tests/plugin/hello_world/tests/action/hello/input.json',
               './tests/plugin/hello_world/tests/action/hello/test_output.json', expect_code=200, is_test=True)


def test_server_test_throw_exeception_action():
    run_action('./tests/plugin/hello_world/tests/action/throw_exception/input.json',
               './tests/plugin/hello_world/tests/action/throw_exception/test_output.json', expect_code=500, is_test=True)
