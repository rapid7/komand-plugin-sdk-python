import komand
from .schema import HelloInput, HelloOutput
import os
import threading
# Custom imports below


class Hello(komand.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
                name='hello',
                description='Print information',
                input=HelloInput(),
                output=HelloOutput())

    def run(self, params={}):
        return {
            'message': 'Hello from Proc {} Thread {}'.format(os.getpid(), threading.current_thread()._name)
        }

    def test(self, params={}):
        return self.run(params)
