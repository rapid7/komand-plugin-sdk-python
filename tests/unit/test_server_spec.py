from insightconnect_plugin_runtime import server
from swagger_spec_validator.validator20 import validate_spec
import json


def test_validate_server_spec():
    plugin_server = server.PluginServer("test")
    with plugin_server.app.test_request_context():
        plugin_server.register_blueprint()
        plugin_server.register_api_spec()

        # Create Swagger Spec
        with open("insightconnect-plugin-swagger.json", "w+") as api_spec:
            api_spec.write(json.dumps(plugin_server.spec.to_dict(), indent=2))
        validate_spec(plugin_server.spec.to_dict())
