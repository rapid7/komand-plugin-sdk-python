import komand
import time
from .schema import ThrowExceptionInput, ThrowExceptionOutput
# Custom imports below


class ThrowException(komand.Trigger):

    def __init__(self):
        super(self.__class__, self).__init__(
                name='throw_exception',
                description='This trigger will always throw an exception as soon as it's invoked',
                input=ThrowExceptionInput(),
                output=ThrowExceptionOutput())

    def run(self, params={}):
        """Run the trigger"""
        while True:
            # TODO: Implement trigger functionality
            self.send({})
            time.sleep(params.get("interval", 5))

    def test(self):
        # TODO: Implement test function
        return {}
