import message
import dispatcher
import logging

class Action(object):
    """A action"""
    def __init__(self, name, description):
        self.connection = None
        self.name = name
        self.description = ''
        self.inputs = {}


    def input(self):
        """ Return input schema for trigger """
        raise NotImplementedError

    def output(self):
        """ Return output schema for trigger """
        raise NotImplementedError

    def run(self):
        """ Run a action, return output or raise error """
        raise NotImplementedError

    def test(self):
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
            output = self.action.test()

            schema = self.action.output()
    
            if schema:
                schema.validate(output)
    

        except Exception as e:
            logging.exception('Action test failure: %s', e)
            err = message.ActionError(
                    meta=self.meta,
                    error=e)
            self.dispatcher.write(err)
            return

        ok = message.ActionSuccess(meta=self.meta, output=output)
        self.dispatcher.write(ok)


    def run(self):
        """ Run the action"""
        try:
            self._setup()
            output = self.action.run()

            schema = self.action.output()
    
            if schema:
                schema.validate(output)

        except Error as e:
            err = message.ActionError(meta=self.meta, error=e)
            self.dispatcher.write(err)
            return

        ok = message.ActionSuccess(meta=self.meta, output=output)
        self.dispatcher.write(ok)


    def _setup(self):
        action_msg = self.msg.get('body')

        if not action_msg:
            raise ValueError('No action input to action task')

        self.meta = action_msg.get('meta') or {}

        if self.connection:
            params = (action_msg.get('connection') or {})
            self.connection.set(params)
            self.connection.connect()
            self.action.connection = self.connection


        input = self.action.input()

        if input:
            inputs = input.validate(action_msg.get('input'))
            self.action.inputs = inputs

