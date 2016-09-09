import sys
import python_jsonschema_objects as pjs
import pprint
import copy
import logging

def default_for_object(obj, defs):
    defaults = {}

    if not obj.get('properties'):
        return defaults

    for key, prop in obj['properties'].iteritems():
        defaults[key] = default_for(prop, defs)
    return defaults

def default_for(prop, defs):

    if 'default' in prop:
        return prop['default']

    # TODO should really follow this
    if prop.get('$ref') and defs:
        items = defs.get(prop.get('$ref'))
        if items:
            return default_for(items, defs)

        return {}

    if not 'type' in prop:
        return ''

    if 'enum' in prop:
        return prop['enum'][0]

    if prop['type'] == 'array':
        return []

    if prop['type'] == 'object':
        return default_for_object(prop, defs)

    if prop['type'] == 'string':
        return ''

    if prop['type'] == 'boolean':
        return False

    if prop['type'] == 'integer' or prop['type'] == 'number':
        return 0

def sample(source):

    if not source or (not 'properties' in source) or len(source['properties']) == 0:
        return {}

    schema = {
                'title': 'Example',
                'properties': {},
                'type': 'object',
                'required': [],
                }

    definitions = {}

    if source.get('definitions'):
        schema['definitions'] = source['definitions']

        for key, defin in source['definitions'].iteritems():
            definitions['#/definitions/' + key] = defin

    defaults = default_for_object(source, definitions)

    for key, prop in source['properties'].iteritems():
        prop = copy.copy(prop)
        schema['properties'][key] = prop
        schema['required'].append(key)

    builder = pjs.ObjectBuilder(schema)
    ns = builder.build_classes()
    Obj = ns.Example
    o = Obj(**defaults)
    return o.as_dict()

def trace(exception):
    """Returns the trace from an exception"""
    return sys.exc_info()[2]

