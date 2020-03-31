from marshmallow.validate import OneOf
from marshmallow import Schema, fields


class PluginInfoSchema(Schema):
    name = fields.Str()
    vendor = fields.Str()
    plugin_spec_version = fields.Str()
    tags = fields.List(fields.Str())
    version = fields.Str()
    title = fields.Str()
    support = fields.Str()
    enable_cache = fields.Bool()
    description = fields.Str()
    number_of_workers = fields.Int()
    threads = fields.Int()


class ActionTriggerOutputBodySchema(Schema):
    log = fields.Str(required=True)
    meta = fields.Dict(required=True)
    output = fields.Dict(required=True)
    status = fields.Str(required=True)


class ActionTriggerOutputSchema(Schema):
    body = fields.Nested(ActionTriggerOutputBodySchema, required=True)
    type = fields.Str(required=True, validate=OneOf(["action_event", "trigger_event"]))
    version = fields.Str(required=True)


class ActionTriggerInputBodySchema(Schema):
    action = fields.Str(required=True)
    connection = fields.Dict(required=True)
    input = fields.Dict(required=True)


class ActionTriggerInputSchema(Schema):
    body = fields.Nested(ActionTriggerInputBodySchema, required=True)
    type = fields.Str(required=True, validate=OneOf(["action_event", "trigger_event"]))
    version = fields.Str(required=True)


class ActionTriggerDetailsSchema(Schema):
    description = fields.Str()
    title = fields.Str()
    input = fields.Dict()
    output = fields.Dict()


class ConnectionDetailsSchema(Schema):
    properties = fields.Dict()
    required = fields.List(fields.Str())
    title = fields.Str()
    type = fields.Str()


class ConnectionTestSchema(Schema):
    message = fields.Dict(required=False)
