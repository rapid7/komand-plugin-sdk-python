# -*- coding: utf-8 -*-
from plugin import run_action, run_trigger


def test_simple_action():
    run_action('./tests/plugin/action/input.json', './tests/plugin/action/output.json')


def test_simple_trigger():
    run_trigger('./tests/plugin/trigger/input.json', './tests/plugin/trigger/output.json')
