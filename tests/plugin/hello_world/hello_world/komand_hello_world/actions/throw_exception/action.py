import komand
from .schema import ThrowExceptionInput, ThrowExceptionOutput
# Custom imports below


class ThrowException(komand.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
                name='throw_exception',
                description='This action will always throw an exception as soon as its invoked',
                input=ThrowExceptionInput(),
                output=ThrowExceptionOutput())

    def run(self, params={}):
        # TODO: Implement run function
        return {}

    def test(self):
        # TODO: Implement test function
        return {}
