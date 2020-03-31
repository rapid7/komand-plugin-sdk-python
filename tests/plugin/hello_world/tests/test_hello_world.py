# -*- coding: utf-8 -*-
from tests.plugin.hello_world import KomandHelloWorld
from tests.plugin import run_action, run_trigger
import pytest

plugin = KomandHelloWorld()


def test_simple_action():
    run_action(
        "./tests/plugin/hello_world/tests/action/hello/input.json",
        "./tests/plugin/hello_world/tests/action/hello/output.json",
        plugin,
    )


def test_simple_trigger():
    run_trigger(
        "./tests/plugin/hello_world/tests/trigger/hello_trigger/input.json",
        "./tests/plugin/hello_world/tests/trigger/hello_trigger/output.json",
        plugin,
    )


def test_bad_action():
    with pytest.raises(Exception):
        run_action(
            "./tests/plugin/hello_world/tests/action/throw_exception/input.json",
            "./tests/plugin/hello_world/tests/action/throw_exception/output.json",
            plugin,
        )


def test_bad_trigger():
    run_trigger(
        "./tests/plugin/hello_world/tests/trigger/throw_exception_trigger/input.json",
        "./tests/plugin/hello_world/tests/trigger/throw_exception_trigger/output.json",
        plugin,
        expect_timeout=True,
    )


def test_bad_json_action():
    with pytest.raises(Exception):
        run_action(
            "./tests/plugin/hello_world/tests/action/return_bad_json/input.json",
            "./tests/plugin/hello_world/tests/action/return_bad_json/output.json",
            plugin,
        )


def test_bad_json_trigger():
    run_trigger(
        "./tests/plugin/hello_world/tests/trigger/return_bad_json_trigger/input.json",
        "./tests/plugin/hello_world/tests/trigger/return_bad_json_trigger/output.json",
        plugin,
        expect_timeout=True,
    )


def test_good_action_bad_input_2():
    run_action(
        "./tests/plugin/hello_world/tests/action/hello/bad_input_2.json",
        "./tests/plugin/hello_world/tests/action/hello/bad_input_2_output.json",
        plugin,
        expect_fail=True,
    )
