import komand
import time
from .schema import ReturnBadJsonInput, ReturnBadJsonOutput
# Custom imports below


class ReturnBadJson(komand.Trigger):

    def __init__(self):
        super(self.__class__, self).__init__(
                name='return_bad_json',
                description='This trigger will return JSON which doesn't match the spec',
                input=ReturnBadJsonInput(),
                output=ReturnBadJsonOutput())

    def run(self, params={}):
        """Run the trigger"""
        while True:
            # TODO: Implement trigger functionality
            self.send({})
            time.sleep(params.get("interval", 5))

    def test(self):
        # TODO: Implement test function
        return {}
