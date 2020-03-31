from insightconnect_plugin_runtime.variables import Input


def test_input_sample():
    schema = {
        "type": "object",
        "properties": {"foo": {"type": "string"}, "bar": {"type": "integer"},},
    }

    i = Input(schema)
    print(i.sample())
