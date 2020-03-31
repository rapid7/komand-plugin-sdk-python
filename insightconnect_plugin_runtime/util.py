# -*- coding: utf-8 -*-
import copy
import sys
import logging

import python_jsonschema_objects as pjs


def default_for_object(obj, defs):
    defaults = {}

    if not obj.get("properties"):
        return defaults

    for key, prop in obj["properties"].items():
        defaults[key] = default_for(prop, defs)
    return defaults


def default_for(prop, defs):
    if "default" in prop:
        return prop["default"]

    # TODO should really follow this
    if prop.get("$ref") and defs:
        items = defs.get(prop.get("$ref"))
        if items:
            return default_for(items, defs)

        return {}

    if "oneOf" in prop:
        for o in prop["oneOf"]:
            t = default_for(o, defs)
            if t is not None:
                return t

    if "type" not in prop:
        return None

    if "enum" in prop:
        return prop["enum"][0]

    if prop["type"] == "array":
        return []

    if prop["type"] == "object":
        return default_for_object(prop, defs)

    if prop["type"] == "string":
        return ""

    if prop["type"] == "boolean":
        return False

    if prop["type"] == "integer" or prop["type"] == "number":
        return 0

    return None


def sample(source):
    if not source or ("properties" not in source) or len(source["properties"]) == 0:
        return {}

    schema = {
        "title": "Example",
        "properties": {},
        "type": "object",
        "required": [],
    }

    definitions = {}

    if source.get("definitions"):
        schema["definitions"] = source["definitions"]

        for key, defin in source["definitions"].items():
            definitions["#/definitions/" + key] = defin

    defaults = default_for_object(source, definitions)

    for key, prop in source["properties"].items():
        prop = copy.copy(prop)
        schema["properties"][key] = prop
        schema["required"].append(key)

    # Get logger instances before sampling runs and suppress them.
    # This will allow us to generate samples WITHOUT having to grep through the debug messages
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for logger in loggers:
        logger.disabled = True

    builder = pjs.ObjectBuilder(schema)
    ns = builder.build_classes(strict=True)
    clazz = ns.Example
    o = clazz(**defaults)

    # Re-enable logging after we're done
    for logger in loggers:
        logger.disabled = False

    return o.as_dict()


def trace():
    """Returns the trace from an exception"""
    return sys.exc_info()[2]
