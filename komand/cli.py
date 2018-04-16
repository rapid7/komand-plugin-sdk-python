# -*- coding: utf-8 -*-

import sys
import argparse
import logging
import komand.message as message
from komand.handler import StepHandler
import json

GREEN = '\033[92m'
RESET = '\033[0m'


class CLI(object):
    """ CLI is a cli for komand """
    def __init__(self, plugin, args=sys.argv[1:]):
        self.plugin = plugin
        self.args = args or []
        self.msg = None
        self.step_handler = StepHandler(plugin)

        if "--" in self.args:
            index = self.args.index("--")
            self.msg = " ".join(self.args[index+1:])
            self.args = self.args[:index]

    def server(self, args):
        if args.debug:
            self.plugin.debug = True

        self.plugin.server(port=args.port)

    def test(self, args):

        if args.debug:
            self.plugin.debug = True

        input_data = sys.stdin
        msg = message.unmarshal(input_data)
        output = self.step_handler.handle_step(msg, is_test=True, is_debug=self.plugin.debug)
        if output:
            sys.stdout.write(json.dumps(output))

    def sample(self, args):
        name = args.name
        trig = self.plugin.triggers.get(name)
        if trig:
            conn = self.plugin.connection
            dispatcher = {'url': 'http://localhost:8000', 'webhook_url': ''}

            if conn:
                conn = conn.sample()
            if trig.input:
                trig.input = trig.input.sample()

            msg = message.trigger_start(
                trigger=trig.name,
                connection=conn,
                input=trig.input,
                dispatcher=dispatcher
            )
            message.marshal(msg, sys.stdout)
            return

        act = self.plugin.actions.get(name)
        if act:
            conn = self.plugin.connection

            if conn:
                conn = conn.sample()
            if act.input:
                act.input = act.input.sample()

            msg = message.action_start(
                action=act.name,
                connection=conn,
                input=act.input
            )
            message.marshal(msg, sys.stdout)
            return

        raise ValueError('Invalid trigger or action name.')

    def info(self, args):
        result = ''
        result += 'Name:        %s%s%s\n' % (GREEN, self.plugin.name, RESET)
        result += 'Vendor:      %s%s%s\n' % (GREEN, self.plugin.vendor, RESET)
        result += 'Version:     %s%s%s\n' % (GREEN, self.plugin.version, RESET)
        result += 'Description: %s%s%s\n' % (GREEN, self.plugin.description, RESET)

        if len(self.plugin.triggers) > 0:
            result += '\n'
            result += 'Triggers (%s%d%s): \n' % (GREEN, len(self.plugin.triggers), RESET)

            for name, item in self.plugin.triggers.items():
                result += '└── %s%s%s (%s%s)\n' % (GREEN, name, RESET, item.description, RESET)

        if len(self.plugin.actions) > 0:
            result += '\n'
            result += 'Actions (%s%d%s): \n' % (GREEN, len(self.plugin.actions), RESET)

            for name, item in self.plugin.actions.items():
                result += '└── %s%s%s (%s%s)\n' % (GREEN, name, RESET, item.description, RESET)

        print(result)

    def _run(self, args):
        if args.debug:
            self.plugin.debug = True

        input_data = sys.stdin
        msg = message.unmarshal(input_data)
        output = self.step_handler.handle_step(msg, is_test=False, is_debug=self.plugin.debug)
        if output:
            sys.stdout.write(json.dumps(output))

    def run(self):
        """Run the CLI tool"""
        parser = argparse.ArgumentParser(description=self.plugin.description)
        parser.add_argument('--version', action='store_true', help='Show version', default=False)
        parser.add_argument('--debug', action='store_true', help='Log events to stdout', default=False)

        subparsers = parser.add_subparsers(help='Commands')

        test_command = subparsers.add_parser('test', help='Run a test using the start message on stdin')
        test_command.set_defaults(func=self.test)

        info_command = subparsers.add_parser('info', help='Display plugin info (triggers and actions).')
        info_command.set_defaults(func=self.info)

        sample_command = subparsers.add_parser('sample',
                                               help='Show a sample start message for the provided trigger or action.')
        sample_command.add_argument('name', help='trigger or action name')
        sample_command.set_defaults(func=self.sample)

        run_command = subparsers.add_parser('run',
                                            help='Run the plugin (default command).'
                                                 'You must supply the start message on stdin.')
        run_command.set_defaults(func=self._run)

        http_command = subparsers.add_parser('http', help='Run a server. ' +
                                                          'You must supply a port, otherwise will listen on 10001.')
        http_command.add_argument('-port', help='--port', default=10001, type=int)
        http_command.set_defaults(func=self.server)

        args = parser.parse_args(self.args)

        if args.debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        if not hasattr(args, 'func') or not args.func:
            return parser.print_help()

        args.func(args)
