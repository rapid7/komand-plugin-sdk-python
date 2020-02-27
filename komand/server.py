import json
import sys
import yaml
import os
import subprocess
import signal

import gunicorn.app.base
from flask import Flask, jsonify, request, abort, make_response
from gunicorn.arbiter import Arbiter
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields
from .exceptions import ClientException, ServerException, LoggedException
from marshmallow.validate import OneOf


API_TITLE = "Runtime API"
API_VERSION = "1.0"
OPEN_API_VERSION = "2.0"


class PluginInfoSchema(Schema):
    name = fields.Str()
    vendor = fields.Str()
    version = fields.Str()
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
    type = fields.Str(required=True, validate=OneOf(['action_event', 'trigger_event']))
    version = fields.Str(required=True)


class ActionTriggerInputBodySchema(Schema):
    action = fields.Str(required=True)
    connection = fields.Dict(required=True)
    input = fields.Dict(required=True)


class ActionTriggerInputSchema(Schema):
    body = fields.Nested(ActionTriggerInputBodySchema, required=True)
    type = fields.Str(required=True, validate=OneOf(['action_event', 'trigger_event']))
    version = fields.Str(required=True)


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
            'bind': '%s:%s' % ('0.0.0.0', port),
            'workers': workers,
            'threads': threads,
            'loglevel': 'debug' if debug else 'info'
        }
        super(PluginServer, self).__init__()
        self.plugin = plugin
        self.debug = debug
        self.app = self.create_flask_app()
        self.workers = workers
        self.threads = threads

        # Create an APISpec
        self.spec = APISpec(
            title=API_TITLE,
            version=API_VERSION,
            openapi_version=OPEN_API_VERSION,
            plugins=[FlaskPlugin(), MarshmallowPlugin()],
        )
        self.master_pid = os.getpid()

    def init(self, parser, opts, args):
        pass

    def load(self):
        return self.app

    def load_config(self):
        config = dict([(key, value) for key, value in self.gunicorn_config.items()
                       if key in self.cfg.settings and value is not None])
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def run_action_trigger(self, input_message, test=False):
        status_code = 200
        output = None
        try:
            output = self.plugin.handle_step(input_message, is_debug=self.debug, is_test=test)
        except LoggedException as e:
            wrapped_exception = e.ex
            self.logger.exception(wrapped_exception)
            output = e.output

            if isinstance(wrapped_exception, ClientException):
                status_code = 400
            elif isinstance(wrapped_exception, ServerException):
                # I'm unsure about this
                status_code = 500
            else:
                status_code = 500
        finally:
            self.logger.debug('Request output: %s', output)
            r = jsonify(output)
            r.status_code = status_code
            return r

    @staticmethod
    def validate_action_trigger(input_message, name, p_type):
        if input_message is None:
            return abort(400)
        if input_message.get('body', {}).get(p_type, None) != name:
            return abort(400)

    def create_flask_app(self):
        app = Flask(__name__)

        @app.route('/actions/<string:name>', methods=['POST'])
        def action_run(name):
            """Run action endpoint.
            ---
            post:
              summary: Run an action
              description: Run an action
              parameters:
                - in: path
                  name: name
                  description: Name of the action
                  type: string
                - in: body
                  name: Action Input
                  description: Input to run an action
                  required: true
                  schema: ActionTriggerInputSchema
              responses:
                200:
                  description: Action output to be returned
                  schema: ActionTriggerOutputSchema
                400:
                  description: Bad request
                500:
                  description: Unexpected error
            """
            input_message = request.get_json(force=True)
            self.logger.debug('Request input: %s', input_message)
            PluginServer.validate_action_trigger(input_message, name, 'action')
            output = self.run_action_trigger(input_message)
            return output

        @app.route('/actions/<string:name>/test', methods=['POST'])
        def action_test(name):
            """Run action test endpoint.
            ---
            post:
              summary: Run action test
              description: Run action test
              parameters:
                - in: path
                  name: name
                  description: Name of the action
                  type: string
                - in: body
                  name: Action Input
                  description: Input to run an action
                  required: true
                  schema: ActionTriggerInputSchema
              responses:
                200:
                  description: Action test output to be returned
                  schema: ActionTriggerOutputSchema
                400:
                  description: Bad request
                500:
                  description: Unexpected error
            """
            input_message = request.get_json(force=True)
            self.logger.debug('Request input: %s', input_message)
            PluginServer.validate_action_trigger(input_message, name, 'action')
            output = self.run_action_trigger(input_message, True)
            return output

        @app.route('/triggers/<string:name>/test', methods=['POST'])
        def trigger_test(name):
            """Run trigger test endpoint.
            ---
            post:
              summary: Run trigger test
              description: Run trigger test
              parameters:
                - in: path
                  name: name
                  description: Name of the trigger
                  type: string
                - in: body
                  name: Trigger Input
                  description: Input to run a trigger
                  required: true
                  schema: ActionTriggerInputSchema
              responses:
                200:
                  description: Trigger test output to be returned
                  schema: ActionTriggerOutputSchema
                400:
                  description: Bad request
                500:
                  description: Unexpected error
            """
            input_message = request.get_json(force=True)
            self.logger.debug('Request input: %s', input_message)
            PluginServer.validate_action_trigger(input_message, name, 'trigger')
            output = self.run_action_trigger(input_message, True)
            return output

        @app.route("/api")
        def api_spec():
            """API spec details endpoint.
            ---
            get:
              summary: Get API spec details
              description: Get Swagger v2.0 API Specification
              parameters:
                - in: query
                  name: format
                  type: string
                  description: Format to return swagger spec; defaults to JSON
                  enum: [json, yaml]
              responses:
                200:
                  description: Swagger Specification to be returned
                  schema:
                    type: object
                422:
                  description: The specified format is not supported
            """
            format_ = request.args.get("format", "json")
            if format_ == "json":
                return json.dumps(self.spec.to_dict())
            elif format_ == "yaml":
                return self.spec.to_yaml()
            else:
                return make_response(jsonify({"error": "The specified format is not supported"}), 422)

        @app.route("/info")
        def plugin_info():
            """Plugin spec details endpoint.
            ---
            get:
              summary: Get plugin details
              description: Get InsightConnect plugin details
              responses:
                200:
                  description: InsightConnect Plugin Information to be returned
                  schema: PluginInfoSchema
            """

            response = {
                "name": self.plugin.name,
                "description": self.plugin.description,
                "version": self.plugin.version,
                "vendor": self.plugin.vendor,
                "number_of_workers": self.workers,
                "threads": self.threads
            }
            return jsonify(PluginInfoSchema().dump(response))

        @app.route("/actions")
        def actions():
            """Plugin actions list endpoint.
            ---
            get:
              summary: Get list of plugin actions
              description: Get InsightConnect plugin all actions
              responses:
                200:
                  description: InsightConnect Plugin actions list to be returned
                  schema:
                    type: array
                    items:
                      type: string
            """
            action_list = []
            for action in self.plugin.actions.keys():
                action_list.append(action)
            return json.dumps(action_list)

        @app.route("/triggers")
        def triggers():
            """Plugin triggers list endpoint.
            ---
            get:
              summary: Get list of plugin triggers
              description: Get InsightConnect plugin all triggers
              responses:
                200:
                  description: InsightConnect Plugin triggers list to be returned
                  schema:
                    type: array
                    items:
                      type: string
            """
            trigger_list = []
            for action in self.plugin.triggers.keys():
                trigger_list.append(action)
            return json.dumps(trigger_list)

        @app.route("/status")
        def status():
            """Web service status endpoint
            ---
            get:
              summary: Get web service status
              description: Get web service status
              responses:
                200:
                  description: Status to be returned
                  schema:
                    type: object
            """
            # TODO: Add logic to figure out status (Ready, Running, Down) of web service.
            return jsonify({"status": "Ready"})

        @app.route("/spec")
        def plugin_spec():
            """Plugin spec details endpoint.
            ---
            get:
              summary: Get plugin spec details
              description: Get plugin specification
              parameters:
                - in: query
                  name: format
                  type: string
                  description: Format to return plugin spec; defaults to JSON
                  enum: [json, yaml]
              responses:
                200:
                  description: Plugin specification to be returned
                  schema:
                    type: object
                422:
                  description: The specified format is not supported
            """
            with open("/python/src/plugin.spec.yaml", "r") as p_spec:
                plugin_spec = p_spec.read()

            format_ = request.args.get("format", "json")

            if format_ == "json":
                return jsonify(yaml.safe_load(plugin_spec))
            elif format_ == "yaml":
                return plugin_spec
            else:
                return make_response(jsonify({"error": "The specified format is not supported"}), 422)

        @app.route("/workers/add", methods=["POST"])
        def add_worker():
            """
            Adds a worker (another process)
            :return: Json Response
            """
            r = {}

            # Linux signal examples here:
            # https://docs.gunicorn.org/en/stable/signals.html#master-process
            try:
                self.logger.info("Adding a worker")
                self.logger.info("Current process is: %s" % self.master_pid)
                os.kill(self.master_pid, signal.SIGTTIN)
            except Exception as e:
                r.status_code = 500
                r.error = e
                return jsonify(r)

            r["num_workers"] = self._number_of_workers()
            return jsonify(r)

        @app.route("/workers/remove", methods=["POST"])
        def remove_worker():
            """
            Shuts down a worker (another process)
            If there is only 1 worker, nothing happens

            :return: Json Response
            """

            r = {}

            # Linux signal examples here:
            # https://docs.gunicorn.org/en/stable/signals.html#master-process
            try:
                self.logger.info("Removing a worker")
                self.logger.info("Current process is: %s" % self.master_pid)
                os.kill(self.master_pid, signal.SIGTTOU)
            except Exception as e:
                r = {}
                r.status_code = 500
                r.error = e
                return jsonify(r)

            return jsonify(r)  # Flask or Gunicorn expect a return

        @app.route("/workers", methods=["GET"])
        def num_workers():
            r = {'num_workers': self._number_of_workers()}
            return jsonify(r)

        # Return flask app
        return app

    def _number_of_workers(self):
        """
        Number of workers tries to return the number of workers in use for gunicorn
        It finds all processes named komand or icon and returns the number it finds minus 1.

        The minus 1 is due to gunicorn always having a master process and at least 1 worker.

        This function will likely produce unreliable results if used outside of a docker container

        :return: integer
        """
        output = subprocess.check_output('ps | grep "icon\\|komand" | grep -v "grep" | wc -l', shell=True)
        num_workers = int(output.decode())

        # num_workers - 1 due to a master process being run as well
        return num_workers - 1

    def register_api_spec(self):
        """ Register all swagger schema definitions and path objects """
        self.spec.components.schema('PluginInfo', schema=PluginInfoSchema)
        self.spec.components.schema('ActionTriggerOutputBody', schema=ActionTriggerOutputBodySchema)
        self.spec.components.schema('ActionTriggerOutput', schema=ActionTriggerOutputSchema)
        self.spec.components.schema('ActionTriggerInputBody', schema=ActionTriggerInputBodySchema)
        self.spec.components.schema('ActionTriggerInput', schema=ActionTriggerInputSchema)
        self.spec.path(view=self.app.view_functions["api_spec"])
        self.spec.path(view=self.app.view_functions["plugin_info"])
        self.spec.path(view=self.app.view_functions["plugin_spec"])
        self.spec.path(view=self.app.view_functions["actions"])
        self.spec.path(view=self.app.view_functions["triggers"])
        self.spec.path(view=self.app.view_functions["status"])
        self.spec.path(view=self.app.view_functions["action_run"])
        self.spec.path(view=self.app.view_functions["action_test"])
        self.spec.path(view=self.app.view_functions["trigger_test"])

    def start(self):
        """ start server """
        with self.app.app_context():
            try:
                arbiter = Arbiter(self)
                self.register_api_spec()
                self.logger = arbiter.log
                arbiter.run()

            except RuntimeError as e:
                sys.stderr.write("\nError: %s\n" % e)
                sys.stderr.flush()
                sys.exit(1)
