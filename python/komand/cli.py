import sys
import argparse

class CLI(object):
    """ CLI is a cli for komand """
    def __init__(self, plugin, args=sys.argv[1:]):
        self.plugin = plugin
        self.args = args

    def test(self, args):
        print("XXXX in test")
        print(args)

    def sample(self, args):
        print("XXXX in sample")
        print(args)

    def info(self, args):
        print("XXXX in info")
        print(args)

    def run(self, args):
        print("XXXX in run")
        print(args)

    def run(self):
        """Run the CLI tool"""
        parser = argparse.ArgumentParser(description=self.plugin.description)
        parser.add_argument('--version', help='Show version', default=False)
        parser.add_argument('--debug', help='Log events to stdout', default=False)

        subparsers = parser.add_subparsers(help='Commands')

        test_command = subparsers.add_parser('test', help='Run a test using the start message on stdin')
        test_command.set_defaults(func=self.test)

        info_command = subparsers.add_parser('info', help='Display plugin info (triggers and actions).')
        info_command.set_defaults(func=self.info)


        sample_command = subparsers.add_parser('sample', help='Show a sample start message for the provided trigger or action.')
        sample_command.add_argument('name', help='trigger or action name')
        sample_command.set_defaults(func=self.sample)

        run_command = subparsers.add_parser('run', help='Run the plugin (default command). You must supply the start message on stdin.')
        run_command.set_defaults(func=self.run)

        args = parser.parse_args(self.args)
        args.func(args)


class Plugin(object):
    def __init__(self):
        self.description = 'VirusTotal'

if __name__ == '__main__':
    cli = CLI(Plugin())
    cli.run()

      
        
        
