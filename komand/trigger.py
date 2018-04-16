# -*- coding: utf-8 -*-
import komand.message as message
from komand.step import Step


class Trigger(Step):
    """A trigger"""

    def __init__(self, name, description, input, output):
        super(Trigger, self).__init__(name, description, input, output)
        self.meta = {}
        self.url = ''
        self.webhook_url = ''
        self.dispatcher = None
        self.log_stream = None

    def send(self, event):
        schema = self.output
        if schema:
            schema.validate(event)

        msg = message.trigger_event(meta=self.meta, output=event, log=self.log_stream.getvalue())
        self.dispatcher.write(msg)
