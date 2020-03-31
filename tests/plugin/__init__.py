import json
import time
import concurrent.futures.thread as thread
import concurrent.futures as futures
from insightconnect_plugin_runtime.exceptions import LoggedException


class CaptureDispatcher:
    def __init__(self):
        self.caught_message = None

    def wait_for_caught_message(self):
        while True:
            if self.caught_message:
                return self.caught_message
            time.sleep(1)

    def write(self, msg):
        self.caught_message = msg


def run_action(input_file, output_file, handler, expect_fail=False):
    input_message = json.load(open(input_file))
    expected_output = json.load(open(output_file))

    try:
        output = handler.handle_step(input_message)
    except LoggedException as e:
        if expect_fail:
            output = e.output
        else:
            raise e

    if "body" in output and "log" in output["body"]:
        output["body"]["log"] = ""

    if "body" in expected_output and "log" in expected_output["body"]:
        expected_output["body"]["log"] = ""

    if output != expected_output:
        raise Exception(
            "Actual output differs from expected output.{} != {}".format(
                output, expected_output
            )
        )


def run_trigger(input_file, output_file, plugin, expect_timeout=False):

    input_message = json.load(open(input_file))
    expected_output = json.load(open(output_file))

    trigger_name = input_message["body"]["trigger"]
    capture = CaptureDispatcher()
    plugin.triggers[trigger_name].dispatcher = capture

    executor = thread.ThreadPoolExecutor()
    executor.submit(plugin.handle_step, input_message)
    future = executor.submit(capture.wait_for_caught_message)
    out = futures.wait([future], timeout=10)
    done = out.done

    # Non-graceful shutdown
    executor._threads.clear()
    futures.thread._threads_queues.clear()

    if len(done) <= 0:
        if expect_timeout:
            return
        raise Exception("Timeout")

    output = capture.caught_message

    if "body" in output and "log" in output["body"]:
        output["body"]["log"] = ""

    if "body" in expected_output and "log" in expected_output["body"]:
        expected_output["body"]["log"] = ""

    if output != expected_output:
        raise Exception(
            "Actual output differs from expected output.{} != {}".format(
                output, expected_output
            )
        )
