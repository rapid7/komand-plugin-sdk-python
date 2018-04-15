# -*- coding: utf-8 -*-
import komand.message as message
import komand.dispatcher as dispatcher
from komand.step import Step
import logging
import sys
import inspect
import six


class Action(Step):
    pass


class Task(object):
    """Task to run or test an action"""
    def __init__(self, connection, action, msg, custom_encoder=None, custom_decoder=None, connection_cache=None,
                 stream=None, dispatch=None):
        if dispatch is None:
            dispatch = dispatcher.Stdout({
                "custom_encoder": custom_encoder,
                "custom_decoder": custom_decoder,
            })
        self.connection = connection
        self.action = action
        self.msg = msg
        self.dispatcher = dispatch
        self.connection_cache = connection_cache
        self.meta = None

    def test(self):
        """ Run test """
        try:
            self._setup(True)
            if six.PY3:
                args = inspect.getfullargspec(self.action.test).args
            else:
                args = inspect.getargspec(self.action.test).args

            if len(args) == 1:
                output = self.action.test()
            else:
                output = self.action.test({})

            schema = self.action.output
            if schema:
                schema.validate(output)

        except Exception as e:
            logging.exception('Action test failure: %s', e)
            err = message.action_error(
                meta=self.meta,
                error=str(e),
                log=self.action.logs())
            self.dispatcher.write(err)
            return False

        success = message.action_success(meta=self.meta, output=output, log=self.action.logs())
        self.dispatcher.write(success)
        return True

    def run(self):
        """ Run the action"""
        try:
            self._setup()
            params = {}
            if self.action and self.action.input.parameters:
                params = self.action.input.parameters
            output = self.action.run(params)

            if self.action.output:
                self.action.output.validate(output)

        except Exception as e:
            logging.exception('Action run failure: %s', e)
            err = message.action_error(meta=self.meta, error=str(e), log=self.action.logs())
            self.dispatcher.write(err)
            sys.exit(1)

        ok = message.action_success(meta=self.meta, output=output, log=self.action.logs())
        self.dispatcher.write(ok)

    def _setup(self, test_mode=False):
        action_msg = self.msg

        if not action_msg:
            raise ValueError('No action input to action task')

        self.meta = action_msg.get('meta') or {}

        conn = None
        params = (action_msg.get('connection') or {})
        if self.connection_cache:
            conn = self.connection_cache.get(params)
        elif self.connection:
            conn = self.connection
            self.connection.set(params)
            self.connection.connect(params)

        self.action.connection = conn
        if self.action.input:
            try:
                self.action.input.set(action_msg.get('input'))
            except Exception as e:
                if not test_mode:
                    raise e
