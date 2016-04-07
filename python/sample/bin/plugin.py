import komand
from ..foobar import *

Name        = 'foobar'
Vendor      = "komand"
Version     = "0.1.0"
Description = "IMAP integration"

class Foobar(komand.Plugin):
    def __init__(self):
        super(self.__class__, self).__init__(name=Name, vendor=Vendor, version=Version,
                description=Description)

        self.add_trigger(triggers.EmitGreeting())
        self.add_action(actions.Respond())

    def connection(self):
        return foobar.Connection()

def main():
    """Run plugin"""
    cli = komand.CLI(Foobar())
    cli.run()

