# -*- coding: utf-8 -*-
from . import KomandHelloWorld
from tests.plugin import run_action, run_trigger

plugin = KomandHelloWorld()


def test_simple_action():
    run_action('./tests/plugin/action/input.json', './tests/plugin/action/output.json', plugin)


def test_simple_trigger():
    run_trigger('./tests/plugin/trigger/input.json', './tests/plugin/trigger/output.json', plugin)
