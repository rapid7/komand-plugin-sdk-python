from komand import server
from swagger_spec_validator.validator20 import validate_spec


def test_validate_server_spec():
    plugin_server = server.PluginServer("test")
    with plugin_server.app.test_request_context():
        plugin_server.register_blueprint()
        plugin_server.register_api_spec()
        validate_spec(plugin_server.spec.to_dict())
