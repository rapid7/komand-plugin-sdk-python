import message
import dispatcher
import logging
import sys

class Action(object):
    """A action"""
    def __init__(self, name, description, input, output):
        self.name = name
        self.description = description 
        self.input = input 
        self.output = output
        self.connection = None

    def run(self, params={}):
        """ Run a action, return output or raise error """
        raise NotImplementedError

    def test(self, params={}):
        """ Test an action, return output or raise error"""
        raise NotImplementedError


class Task(object):
    """Task to run or test an action"""
    def __init__(self, connection, action, msg, dispatch=dispatcher.Stdout()):
        self.connection = connection
        self.action = action
        self.msg = msg
        self.dispatcher = dispatch
        self.meta = None


    def test(self):
        """ Run test """
        try:
            self._setup()
            params = {}
            if self.action and self.action.input.parameters:
                params = self.action.input.parameters

            output = self.action.test(params)
            schema = self.action.output
    
            if schema:
                schema.validate(output)
    

        except Exception as e:
            logging.exception('Action test failure: %s', e)
            err = message.ActionError(
                    meta=self.meta,
                    error=str(e))
            self.dispatcher.write(err)
            return

        ok = message.ActionSuccess(meta=self.meta, output=output)
        self.dispatcher.write(ok)


    def run(self):
        """ Run the action"""
        try:
            self._setup()
            params = {}
            if self.action and self.action.input.parameters:
                params = self.action.input.parameters
            output = self.action.run(params)

            schema = self.action.output
    
            if schema:
                schema.validate(output)
        except Exception as e:
            logging.exception('Action run failure: %s', e)
            err = message.ActionError(meta=self.meta, error=str(e))
            self.dispatcher.write(err)
            return

        ok = message.ActionSuccess(meta=self.meta, output=output)
        self.dispatcher.write(ok)


    def _setup(self):
        action_msg = self.msg

        if not action_msg:
            raise ValueError('No action input to action task')

        self.meta = action_msg.get('meta') or {}

        if self.connection:
            params = (action_msg.get('connection') or {})
            self.connection.set(params)
            import inspect
            print inspect.getsource(self.connection.connect)
            self.connection.connect(params)
            self.action.connection = self.connection


        input = self.action.input

        if input:
            input.set(action_msg.get('input'))

