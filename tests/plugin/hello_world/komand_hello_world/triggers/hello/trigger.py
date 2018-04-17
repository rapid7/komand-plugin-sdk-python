import komand
import time
from .schema import HelloInput, HelloOutput
# Custom imports below


class Hello(komand.Trigger):

    def __init__(self):
        super(self.__class__, self).__init__(
                name='hello',
                description='Prints a greeting every 10 seconds',
                input=HelloInput(),
                output=HelloOutput())

    def run(self, params={}):
        """Run the trigger"""
        while True:
            # TODO: Implement trigger functionality
            self.send({})
            time.sleep(params.get("interval", 5))

    def test(self):
        # TODO: Implement test function
        return {}
