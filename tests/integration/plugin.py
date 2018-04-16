import komand
import komand.handler
import json
import time

import concurrent.futures.thread as thread
import concurrent.futures as futures


connection_schema = {
    'type': 'object',
    'properties': {
        'greeting': {
            'type': 'string'
        }
    },
    'required': ['greeting']
}

input_schema = {
    'type': 'object',
    'properties': {
        'name': {
            'type': 'string'
        }
    },
    'required': ['name']
}

output_schema = {
    'type': 'object',
    'properties': {
        'text': {
            'type': 'string'
        }
    },
    'required': ['text']
}


class Connection(komand.Connection):
    def __init__(self):
        super(self.__class__, self).__init__(komand.Input(connection_schema))
        self.greeting = None

    def connect(self, params={}):
        self.greeting = params.get('greeting', 'no greeting for {}')


class Action(komand.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name='action',
            description='description',
            input=komand.Input(schema=input_schema),
            output=komand.Output(schema=output_schema)
        )

    def run(self, params={}):
        self.logger.info(u'I am the log')
        return {
            'text': self.connection.greeting.format(params['name'])
        }

    def test(self, params={}):
        self.logger.info(u'This was a test')
        return {
            'text': 'Test greeting'
        }


class Trigger(komand.Trigger):

    def __init__(self):
        super(self.__class__, self).__init__(
            name='trigger',
            description='description',
            input=komand.Input(schema=input_schema),
            output=komand.Output(schema=output_schema)
        )

    def run(self, params={}):
        while True:
            self.logger.info(u'I am the log')
            self.send({
                'text': self.connection.greeting.format(params['name'])
            })
            time.sleep(10)

    def test(self, params={}):
        self.logger.info(u'This was a test')
        return {
            'text': 'Test greeting'
        }


class Plugin(komand.Plugin):
    def __init__(self):
        super(self.__class__, self).__init__(
            name='HelloWorld',
            vendor='komand',
            version='1.0.0',
            description='Hello World plugin',
            connection=Connection()
        )

        self.add_action(Action())

        self.add_trigger(Trigger())


plugin = Plugin()
handler = komand.handler.StepHandler(plugin)


caught_message = None


def wait_for_caught_message():
    while True:
        if caught_message:
            return caught_message
        time.sleep(1)


class CaptureDispatcher:

    def write(self, msg):
        global caught_message
        caught_message = msg


plugin.triggers['trigger'].dispatcher = CaptureDispatcher()


def run_action(input_file, output_file):
    input_message = json.load(open(input_file))
    expected_output = json.load(open(output_file))
    output = handler.handle_step(input_message)
    assert output == expected_output


def run_trigger(input_file, output_file):
    input_message = json.load(open(input_file))
    expected_output = json.load(open(output_file))

    executor = thread.ThreadPoolExecutor()
    executor.submit(handler.handle_step, input_message)
    future = executor.submit(wait_for_caught_message)
    out = futures.wait([future], timeout=10)
    done = out.done

    # Non-graceful shutdown
    executor._threads.clear()
    futures.thread._threads_queues.clear()

    if len(done) <= 0:
        raise Exception('Timeout')

    assert caught_message == expected_output
