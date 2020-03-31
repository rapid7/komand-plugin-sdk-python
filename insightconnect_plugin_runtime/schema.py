import json

import pkg_resources


def load_schema(file_name):
    """
    Loads a json schema from the packages data folder.
    :param file_name: name of the file
    :return: JSON object as a dictionary
    """

    schema = pkg_resources.resource_stream(__name__, "/".join(("data", file_name)))
    schema = schema.read()
    if isinstance(schema, bytes):
        schema = schema.decode("utf-8")
    schema = json.loads(schema)
    return schema


input_message_schema = load_schema("input_message_schema.json")
output_message_schema = load_schema("output_message_schema.json")
