# -*- coding: utf-8 -*-
import sys

import argparse

from .exceptions import LoggedException
from .server import PluginServer

GREEN = "\033[92m"
RESET = "\033[0m"


class CLI(object):
    """
    A command line interface for the komand plugin CLI API.

    komand plugins are launched via the command line.

    Parameters:
     - info:   Display plugin info message
     - sample: Output a sample input JSON object for an action/trigger (step name 2nd parameter)
     - run:    Execute run method of an action/trigger
     - test:   Execute test method of an action/trigger
     - http:   Launch plugin in server mode

    Legacy mode:
     - read input JSON from stdin
     - output logs to stderr
     - output result JSON to stdout

    Server mode:
     - the 'http' parameter starts the plugin in server mode
     - HTTP POST requests replace the stdin/stdout communication
     - test mode is set via path component, ie. POST host:port/actions/action_name/test
    """

    def __init__(self, plugin, args=sys.argv[1:]):
        self.plugin = plugin
        self.args = args or []
        self.msg = None

        if "--" in self.args:
            index = self.args.index("--")
            self.msg = " ".join(self.args[index + 1 :])
            self.args = self.args[:index]

    def info(self, args):
        result = ""
        result += "Name:        %s%s%s\n" % (GREEN, self.plugin.name, RESET)
        result += "Vendor:      %s%s%s\n" % (GREEN, self.plugin.vendor, RESET)
        result += "Version:     %s%s%s\n" % (GREEN, self.plugin.version, RESET)
        result += "Description: %s%s%s\n" % (GREEN, self.plugin.description, RESET)

        if len(self.plugin.triggers) > 0:
            result += "\n"
            result += "Triggers (%s%d%s):\n" % (GREEN, len(self.plugin.triggers), RESET)

            for name, item in self.plugin.triggers.items():
                result += "└── %s%s%s (%s%s)\n" % (
                    GREEN,
                    name,
                    RESET,
                    item.description,
                    RESET,
                )

        if len(self.plugin.actions) > 0:
            result += "\n"
            result += "Actions (%s%d%s):\n" % (GREEN, len(self.plugin.actions), RESET)

            for name, item in self.plugin.actions.items():
                result += "└── %s%s%s (%s%s)\n" % (
                    GREEN,
                    name,
                    RESET,
                    item.description,
                    RESET,
                )

        print(result)

    def sample(self, args):
        name = args.name
        trig = self.plugin.triggers.get(name)
        if trig:
            conn = self.plugin.connection
            dispatcher = {"url": "http://localhost:8000", "webhook_url": ""}
            input = None
            if conn:
                conn = conn.sample()
            if trig.input:
                input = trig.input.sample()

            msg = {
                "body": {
                    "trigger": trig.name,
                    "meta": {},
                    "input": input,
                    "dispatcher": dispatcher,
                    "connection": conn,
                },
                "type": "trigger_start",
                "version": "v1",
            }

            self.plugin.marshal(msg, sys.stdout)
            return

        act = self.plugin.actions.get(name)
        if act:
            conn = self.plugin.connection
            input = None
            if conn:
                conn = conn.sample()
            if act.input:
                input = act.input.sample()

            msg = {
                "body": {
                    "action": act.name,
                    "meta": {},
                    "input": input,
                    "connection": conn,
                },
                "type": "action_start",
                "version": "v1",
            }
            self.plugin.marshal(msg, sys.stdout)
            return

        raise ValueError("Invalid trigger or action name.")

    def execute_step(self, is_test=False, is_debug=False, msg=None):
        if not msg:
            msg = self.plugin.unmarshal(sys.stdin)
        exception = None
        try:
            output = self.plugin.handle_step(msg, is_test=is_test, is_debug=is_debug)
        except LoggedException as e:
            output = e.output
            exception = e

        if output:
            self.plugin.marshal(output, sys.stdout)

        if exception:
            raise exception

    def run_step(self, args):
        return self.execute_step(is_test=False, is_debug=args.debug)

    def test_step(self, args):
        return self.execute_step(is_test=True, is_debug=args.debug)

    def server(self, args):
        if args.debug:
            self.plugin.debug = True

        PluginServer(
            self.plugin,
            port=args.port,
            workers=args.process_workers,
            threads=args.threads_per_worker,
            debug=args.debug,
        ).start()

    def run(self):
        """Run the CLI tool"""
        parser = argparse.ArgumentParser(description=self.plugin.description)
        parser.add_argument(
            "--version", action="store_true", help="Show version", default=False
        )
        parser.add_argument(
            "--debug", action="store_true", help="Log events to stdout", default=False
        )

        subparsers = parser.add_subparsers(help="Commands")

        test_command = subparsers.add_parser(
            "test", help="Run a test using the start message on stdin"
        )
        test_command.set_defaults(func=self.test_step)

        info_command = subparsers.add_parser(
            "info", help="Display plugin info (triggers and actions)."
        )
        info_command.set_defaults(func=self.info)

        sample_command = subparsers.add_parser(
            "sample",
            help="Show a sample start message for the provided trigger or action.",
        )
        sample_command.add_argument("name", help="trigger or action name")
        sample_command.set_defaults(func=self.sample)

        run_command = subparsers.add_parser(
            "run",
            help="Run the plugin (default command)."
            "You must supply the start message on stdin.",
        )
        run_command.set_defaults(func=self.run_step)

        http_command = subparsers.add_parser(
            "http",
            help="Run a server. "
            + "You must supply a port, otherwise will listen on 10001.",
        )
        http_command.add_argument("--port", help="--port", default=10001, type=int)
        http_command.add_argument(
            "--process_workers",
            help="The number of child processes to spawn",
            default=1,
            type=int,
        )
        http_command.add_argument(
            "--threads_per_worker",
            help="The number of threads per worker process",
            default=4,
            type=int,
        )
        http_command.set_defaults(func=self.server)

        args = parser.parse_args(self.args)

        if not hasattr(args, "func") or not args.func:
            return parser.print_help()

        args.func(args)
