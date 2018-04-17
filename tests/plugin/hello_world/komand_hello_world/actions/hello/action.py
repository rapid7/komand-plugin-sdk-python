import komand
from .schema import HelloInput, HelloOutput
# Custom imports below


class Hello(komand.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
                name='hello',
                description='Print hello world',
                input=HelloInput(),
                output=HelloOutput())

    def run(self, params={}):
        # TODO: Implement run function
        return {}

    def test(self):
        # TODO: Implement test function
        return {}
