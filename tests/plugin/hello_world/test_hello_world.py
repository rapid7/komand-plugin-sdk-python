# -*- coding: utf-8 -*-
from . import KomandHelloWorld
from tests.plugin import run_action, run_trigger
from komand.handler import StepHandler

plugin = KomandHelloWorld()
handler = StepHandler(plugin)


def test_simple_action():
    run_action('./tests/plugin/action/input.json', './tests/plugin/action/output.json', handler)


def test_simple_trigger():
    run_trigger('./tests/plugin/trigger/input.json', './tests/plugin/trigger/output.json', handler)
