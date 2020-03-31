import os
import sys
import gunicorn.app.base
from flask import Flask
from gunicorn.arbiter import Arbiter
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from insightconnect_plugin_runtime.api.schemas import (
    PluginInfoSchema,
    ActionTriggerOutputBodySchema,
    ActionTriggerOutputSchema,
    ActionTriggerInputBodySchema,
    ActionTriggerInputSchema,
    ActionTriggerDetailsSchema,
    ConnectionDetailsSchema,
    ConnectionTestSchema,
)
from insightconnect_plugin_runtime.api.endpoints import Endpoints

API_TITLE = "InsightConnect Plugin Runtime API"
API_VERSION = "1.0"
OPEN_API_VERSION = "2.0"
VERSION_MAPPING = {"legacy": "/", "v1": "/api/v1"}


class PluginServer(gunicorn.app.base.BaseApplication):
    """
    Server which runs the plugin as an HTTP server.

    Serves the following endpoints:

    POST http://host/actions/[action]        Executes action's run method
    POST http://host/actions/[action]/test   Executes action's test method
    POST http://host/triggers/[trigger]/test Executes trigger's test method

    NOTE: starting a trigger is not supported. Triggers should be started in legacy mode.

    """

    def __init__(self, plugin, port=10001, workers=1, threads=4, debug=False):
        self.gunicorn_config = {
            "bind": "%s:%s" % ("0.0.0.0", port),
            "workers": workers,
            "threads": threads,
            "loglevel": "debug" if debug else "info",
        }
        super(PluginServer, self).__init__()
        self.plugin = plugin
        self.arbiter = Arbiter(self)
        self.logger = self.arbiter.log
        self.debug = debug
        # Create an APISpec
        self.spec = APISpec(
            title=API_TITLE,
            version=API_VERSION,
            openapi_version=OPEN_API_VERSION,
            plugins=[FlaskPlugin(), MarshmallowPlugin()],
        )
        self.workers = workers
        self.threads = threads
        self.app, self.blueprints = self.create_flask_app()

    def init(self, parser, opts, args):
        pass

    def load(self):
        return self.app

    def load_config(self):
        config = dict(
            [
                (key, value)
                for key, value in self.gunicorn_config.items()
                if key in self.cfg.settings and value is not None
            ]
        )
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def create_flask_app(self):
        app = Flask(__name__)
        endpoints = Endpoints(
            self.logger,
            self.plugin,
            self.spec,
            self.debug,
            self.workers,
            self.threads,
            os.getpid(),
        )
        blueprints = endpoints.create_endpoints()
        # Return flask app and list of blueprints
        return app, blueprints

    def register_api_spec(self):
        """ Register all swagger schema definitions and path objects """
        self.spec.components.schema("PluginInfo", schema=PluginInfoSchema)
        self.spec.components.schema(
            "ActionTriggerOutputBody", schema=ActionTriggerOutputBodySchema
        )
        self.spec.components.schema(
            "ActionTriggerOutput", schema=ActionTriggerOutputSchema
        )
        self.spec.components.schema(
            "ActionTriggerInputBody", schema=ActionTriggerInputBodySchema
        )
        self.spec.components.schema(
            "ActionTriggerInput", schema=ActionTriggerInputSchema
        )
        self.spec.components.schema(
            "ActionTriggerDetails", schema=ActionTriggerDetailsSchema
        )
        self.spec.components.schema("ConnectionDetails", schema=ConnectionDetailsSchema)
        self.spec.components.schema("ConnectionTestOutput", schema=ConnectionTestSchema)
        self.spec.path(view=self.app.view_functions["v1.api_spec"])
        self.spec.path(view=self.app.view_functions["v1.plugin_info"])
        self.spec.path(view=self.app.view_functions["v1.plugin_spec"])
        self.spec.path(view=self.app.view_functions["v1.actions"])
        self.spec.path(view=self.app.view_functions["v1.triggers"])
        self.spec.path(view=self.app.view_functions["v1.status"])
        self.spec.path(view=self.app.view_functions["v1.action_run"])
        self.spec.path(view=self.app.view_functions["v1.action_test"])
        self.spec.path(view=self.app.view_functions["v1.trigger_test"])
        self.spec.path(view=self.app.view_functions["v1.action_details"])
        self.spec.path(view=self.app.view_functions["v1.trigger_details"])
        self.spec.path(view=self.app.view_functions["v1.connection"])
        self.spec.path(view=self.app.view_functions["v1.connection_test"])

    def register_blueprint(self):
        """Register all blueprints"""
        for blueprint in self.blueprints:
            self.app.register_blueprint(
                blueprint, url_prefix=VERSION_MAPPING[blueprint.name]
            )

    def start(self):
        """ start server """
        with self.app.app_context():
            try:
                self.register_blueprint()
                self.register_api_spec()
                self.arbiter.run()
            except RuntimeError as e:
                sys.stderr.write("\nError: %s\n" % e)
                sys.stderr.flush()
                sys.exit(1)
