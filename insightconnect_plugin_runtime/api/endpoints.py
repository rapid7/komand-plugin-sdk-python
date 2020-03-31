import json
import subprocess
import yaml
import os
import signal
from flask import jsonify, request, abort, make_response, Blueprint
from insightconnect_plugin_runtime.exceptions import (
    ClientException,
    ServerException,
    LoggedException,
    ConnectionTestException,
)
from insightconnect_plugin_runtime.api.schemas import (
    PluginInfoSchema,
    ActionTriggerDetailsSchema,
    ConnectionDetailsSchema,
)


class Endpoints:
    def __init__(self, logger, plugin, spec, debug, workers, threads, master_pid):
        self.plugin = plugin
        self.logger = logger
        self.spec = spec
        self.debug = debug
        self.workers = workers
        self.threads = threads
        self.master_pid = master_pid

    def create_endpoints(self):
        legacy = Blueprint("legacy", __name__)
        v1 = Blueprint("v1", __name__)

        @v1.route("/actions/<string:name>", methods=["POST"])
        @legacy.route("/actions/<string:name>", methods=["POST"])
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
            self.logger.debug("Request input: %s", input_message)
            Endpoints.validate_action_trigger_empty_input(input_message)
            Endpoints.validate_action_trigger_name(input_message, name, "action")
            output = self.run_action_trigger(input_message)
            return output

        @legacy.route("/triggers/<string:name>/test", methods=["POST"])
        @v1.route("/triggers/<string:name>/test", methods=["POST"])
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
            self.logger.debug("Request input: %s", input_message)
            Endpoints.validate_action_trigger_empty_input(input_message)
            Endpoints.validate_action_trigger_name(input_message, name, "trigger")
            output = self.run_action_trigger(input_message, True)
            return output

        @legacy.route("/actions/<string:name>/test", methods=["POST"])
        @v1.route("/actions/<string:name>/test", methods=["POST"])
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
            self.logger.debug("Request input: %s", input_message)
            Endpoints.validate_action_trigger_empty_input(input_message)
            Endpoints.validate_action_trigger_name(input_message, name, "action")
            output = self.run_action_trigger(input_message, True)
            return output

        @v1.route("/api")
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
                return make_response(
                    jsonify({"error": "The specified format is not supported"}), 422
                )

        @v1.route("/info")
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
            plugin_spec_json = Endpoints.load_file_json_format(
                "/python/src/plugin.spec.yaml"
            )
            plugin_info_fields = [
                "name",
                "description",
                "version",
                "vendor",
                "plugin_spec_version",
                "title",
                "support",
                "tags",
                "enable_cache",
            ]
            response = Endpoints.get_plugin_info(plugin_spec_json, plugin_info_fields)
            # Add workers and threads
            response.update(
                {"number_of_workers": self.workers, "threads": self.threads}
            )
            return jsonify(PluginInfoSchema().dump(response))

        @v1.route("/actions")
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
            return jsonify(action_list)

        @v1.route("/actions/<string:name>")
        def action_details(name):
            """Get action details endpoint.
             ---
             get:
               summary: Retrieve action details
               description: Retrieve action details
               parameters:
                 - in: path
                   name: name
                   description: Name of the action
                   type: string
               responses:
                 200:
                   description: Action details to be returned
                   schema: ActionTriggerDetailsSchema
                 400:
                   description: Bad request
             """
            plugin_spec_json = Endpoints.load_file_json_format(
                "/python/src/plugin.spec.yaml"
            )
            Endpoints.action_trigger_exists(plugin_spec_json, "actions", name)
            return jsonify(
                ActionTriggerDetailsSchema().dump(
                    plugin_spec_json.get("actions").get(name)
                )
            )

        @v1.route("/triggers/<string:name>")
        def trigger_details(name):
            """Get trigger details endpoint.
             ---
             get:
               summary: Retrieve trigger details
               description: Retrieve trigger details
               parameters:
                 - in: path
                   name: name
                   description: Name of the trigger
                   type: string
               responses:
                 200:
                   description: Trigger details to be returned
                   schema: ActionTriggerDetailsSchema
                 400:
                   description: Bad request
             """
            plugin_spec_json = Endpoints.load_file_json_format(
                "/python/src/plugin.spec.yaml"
            )
            Endpoints.action_trigger_exists(plugin_spec_json, "triggers", name)
            return jsonify(
                ActionTriggerDetailsSchema().dump(
                    plugin_spec_json.get("triggers").get(name)
                )
            )

        @v1.route("/triggers")
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
            return jsonify(trigger_list)

        @v1.route("/status")
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

        @v1.route("/spec")
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
            format_ = request.args.get("format", "json")
            if format_ not in ["json", "yaml"]:
                return make_response(
                    jsonify({"error": "The specified format is not supported"}), 422
                )

            with open("/python/src/plugin.spec.yaml", "r") as p_spec:
                plugin_spec = p_spec.read()

            if format_ == "yaml":
                return plugin_spec
            return jsonify(yaml.safe_load(plugin_spec))

        @v1.route("/workers/add", methods=["POST"])
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

            r["num_workers"] = Endpoints._number_of_workers()
            return jsonify(r)

        @v1.route("/workers/remove", methods=["POST"])
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

        @v1.route("/workers", methods=["GET"])
        def num_workers():
            r = {"num_workers": Endpoints._number_of_workers()}
            return jsonify(r)

        @v1.route("/connection", methods=["GET"])
        def connection():
            """Plugin connection details endpoint
            ---
            get:
              summary: Get plugin connection details
              description: Get InsightConnect plugin connection details
              responses:
                200:
                  description: InsightConnect plugin connection details to be returned
                  schema: ConnectionDetailsSchema
            """
            conn = self.plugin.connection
            schema = conn.schema
            return jsonify(ConnectionDetailsSchema().dump(schema))

        @v1.route("/connection/test", methods=["POST"])
        def connection_test():
            """Run connection test endpoint
            ---
            post:
              summary: Run connection test
              description: Run InsightConnect plugin connection test
              responses:
                200:
                  description: Connection test output to be returned
                  schema: ConnectionTestSchema
                204:
                  description: The server successfully processed the request and is not returning any content
                400:
                  description: A ConnectionTestException has occurred
                500:
                  description: Internal server error
            """
            status_code = 200
            message = None
            try:
                if hasattr(self.plugin.connection, "test"):
                    response = self.plugin.connection.test()
                    if response is None:
                        status_code = 204
                        message = "The server successfully processed the request and is not returning any content"
                    else:
                        message = response
                else:
                    status_code = 204
                    message = "The server successfully processed the request and is not returning any content"
            except Exception as e:
                if isinstance(e, ConnectionTestException):
                    status_code = 400
                    message = e.data
                else:
                    status_code = 500
                    message = str(e)
            finally:
                output = make_response(jsonify({"message": message}), status_code)
                return output

        blueprints = [legacy, v1]
        return blueprints

    @staticmethod
    def _number_of_workers():
        """
        Number of workers tries to return the number of workers in use for gunicorn
        It finds all processes named komand or icon and returns the number it finds minus 1.

        The minus 1 is due to gunicorn always having a master process and at least 1 worker.

        This function will likely produce unreliable results if used outside of a docker container

        :return: integer
        """
        output = subprocess.check_output(
            'ps | grep "icon\\|komand" | grep -v "grep" | wc -l', shell=True
        )
        num_workers = int(output.decode())

        # num_workers - 1 due to a master process being run as well
        return num_workers - 1

    @staticmethod
    def action_trigger_exists(plugin_spec_json, p_type, p_name):
        actions_triggers = plugin_spec_json.get(p_type)
        if actions_triggers is None or actions_triggers.get(p_name) is None:
            msg = f"{p_type[:-1].capitalize()} {p_name} does not exists"
            resp = make_response(jsonify({"error": msg}), 400)
            abort(resp)
        return actions_triggers.get(p_name)

    @staticmethod
    def load_file_json_format(filename):
        with open(filename, "r") as p_spec:
            return yaml.safe_load(p_spec.read())

    @staticmethod
    def validate_action_trigger_empty_input(input_message):
        if not input_message:
            resp = make_response(jsonify({"error": "Empty input provided"}), 400)
            abort(resp)

    @staticmethod
    def validate_action_trigger_name(input_message, name, p_type):
        name_in_input_msg = input_message.get("body", {}).get(p_type, None)
        if name_in_input_msg != name:
            msg = f"Action name ({name_in_input_msg}) in input body is not matching with name ({name}) in route"
            resp = make_response(jsonify({"error": msg}), 400)
            abort(resp)

    @staticmethod
    def get_plugin_info(plugin_spec_json, fields):
        plugin_info = {}
        for field in fields:
            plugin_info.update({field: plugin_spec_json.get(field)})
        return plugin_info

    def run_action_trigger(self, input_message, test=False):
        status_code = 200
        output = None
        try:
            output = self.plugin.handle_step(
                input_message, is_debug=self.debug, is_test=test
            )
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
            self.logger.debug("Request output: %s", output)
            r = jsonify(output)
            r.status_code = status_code
            return r
