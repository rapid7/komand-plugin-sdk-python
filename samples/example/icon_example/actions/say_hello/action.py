import komand
from .schema import SayHelloInput, SayHelloOutput, Input, Output, Component
# Custom imports below


class SayHello(komand.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
                name='say_hello',
                description=Component.DESCRIPTION,
                input=SayHelloInput(),
                output=SayHelloOutput())

    def run(self, params={}):
        return {Output.MESSAGE: f"Hello, {params.get(Input.NAME)}"}
