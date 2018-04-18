# -*- coding: utf-8 -*-
import sys
import argparse
from .message import trigger_start, marshal, action_start, unmarshal
import json


GREEN = '\033[92m'
RESET = '\033[0m'


class CLI(object):
    """ CLI is a cli for komand """

    def __init__(self, plugin, args=sys.argv[1:]):
        self.plugin = plugin
        self.args = args or []
        self.msg = None

        if "--" in self.args:
            index = self.args.index("--")
            self.msg = " ".join(self.args[index+1:])
            self.args = self.args[:index]

    def info(self, args):
        result = ''
        result += 'Name:        %s%s%s\n' % (GREEN, self.plugin.name, RESET)
        result += 'Vendor:      %s%s%s\n' % (GREEN, self.plugin.vendor, RESET)
        result += 'Version:     %s%s%s\n' % (GREEN, self.plugin.version, RESET)
        result += 'Description: %s%s%s\n' % (GREEN, self.plugin.description, RESET)

        if len(self.plugin.triggers) > 0:
            result += '\n'
            result += 'Triggers (%s%d%s):\n' % (GREEN, len(self.plugin.triggers), RESET)

            for name, item in self.plugin.triggers.items():
                result += '└── %s%s%s (%s%s)\n' % (GREEN, name, RESET, item.description, RESET)

        if len(self.plugin.actions) > 0:
            result += '\n'
            result += 'Actions (%s%d%s):\n' % (GREEN, len(self.plugin.actions), RESET)

            for name, item in self.plugin.actions.items():
                result += '└── %s%s%s (%s%s)\n' % (GREEN, name, RESET, item.description, RESET)

        print(result)

    def sample(self, args):
        name = args.name
        trig = self.plugin.triggers.get(name)
        if trig:
            conn = self.plugin.connection
            dispatcher = {'url': 'http://localhost:8000', 'webhook_url': ''}
            input = None
            if conn:
                conn = conn.sample()
            if trig.input:
                input = trig.input.sample()

            msg = trigger_start(
                trigger=trig.name,
                connection=conn,
                input=input,
                dispatcher=dispatcher
            )
            marshal(msg, sys.stdout)
            return

        act = self.plugin.actions.get(name)
        if act:
            conn = self.plugin.connection
            input = None
            if conn:
                conn = conn.sample()
            if act.input:
                input = act.input.sample()

            msg = action_start(
                action=act.name,
                connection=conn,
                input=input
            )
            marshal(msg, sys.stdout)
            return

        raise ValueError('Invalid trigger or action name.')

    def execute_step(self, is_test=False, is_debug=False):
        input_data = sys.stdin
        msg = unmarshal(input_data)
        ret = 0
        output = None
        try:
            output = self.plugin.handle_step(msg, is_test=is_test, is_debug=is_debug)
        except Exception as e:
            ret = 1

        if output:
            sys.stdout.write(json.dumps(output))
        return ret

    def run_step(self, args):
        return self.execute_step(is_test=False, is_debug=args.debug)

    def test_step(self, args):
        return self.execute_step(is_test=True, is_debug=args.debug)

    def server(self, args):
        if args.debug:
            self.plugin.debug = True

        self.plugin.server(port=args.port)

    def run(self):
        """Run the CLI tool"""
        parser = argparse.ArgumentParser(description=self.plugin.description)
        parser.add_argument('--version', action='store_true', help='Show version', default=False)
        parser.add_argument('--debug', action='store_true', help='Log events to stdout', default=False)

        subparsers = parser.add_subparsers(help='Commands')

        test_command = subparsers.add_parser('test', help='Run a test using the start message on stdin')
        test_command.set_defaults(func=self.test_step)

        info_command = subparsers.add_parser('info', help='Display plugin info (triggers and actions).')
        info_command.set_defaults(func=self.info)

        sample_command = subparsers.add_parser('sample',
                                               help='Show a sample start message for the provided trigger or action.')
        sample_command.add_argument('name', help='trigger or action name')
        sample_command.set_defaults(func=self.sample)

        run_command = subparsers.add_parser('run',
                                            help='Run the plugin (default command).'
                                                 'You must supply the start message on stdin.')
        run_command.set_defaults(func=self.run_step)

        http_command = subparsers.add_parser('http', help='Run a server. ' +
                                                          'You must supply a port, otherwise will listen on 10001.')
        http_command.add_argument('-port', help='--port', default=10001, type=int)
        http_command.set_defaults(func=self.server)

        args = parser.parse_args(self.args)

        if not hasattr(args, 'func') or not args.func:
            return parser.print_help()

        return args.func(args)
