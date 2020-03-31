# -*- coding: utf-8 -*-
from tests.plugin.hello_world import KomandHelloWorld
from insightconnect_plugin_runtime import CLI
from insightconnect_plugin_runtime.server import PluginServer
import pytest


@pytest.fixture(scope="module")
def plugin_server():
    # Initialize plugin
    cli = CLI(KomandHelloWorld())
    plugin = PluginServer(cli.plugin, port=10001, workers=1, threads=4, debug=False,)

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = plugin.app.test_client()

    # Register blueprints and spec
    # TODO: do this outside of test in future
    with plugin.app.app_context():
        plugin.register_blueprint()
        plugin.register_api_spec()

    # Establish an application context before running tests
    ctx = plugin.app.app_context()
    ctx.push()

    # Allow tests to run and provide client
    yield testing_client

    # Cleanup application context
    ctx.pop()
