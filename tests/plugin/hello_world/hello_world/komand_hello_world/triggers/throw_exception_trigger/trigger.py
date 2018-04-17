import komand
import time
from .schema import ThrowExceptionTriggerInput, ThrowExceptionTriggerOutput
# Custom imports below


class ThrowExceptionTrigger(komand.Trigger):

    def __init__(self):
        super(self.__class__, self).__init__(
                name='throw_exception_trigger',
                description='This trigger will always throw an exception as soon as its invoked',
                input=ThrowExceptionTriggerInput(),
                output=ThrowExceptionTriggerOutput())

    def run(self, params={}):
        """Run the trigger"""
        while True:
            # TODO: Implement trigger functionality
            self.send({})
            time.sleep(params.get("interval", 5))

    def test(self):
        # TODO: Implement test function
        return {}
