class ClientException(Exception):
    """
    An exception which marks an error made by the plugin invoker.

    Some examples of when to use this are:
    - Malformed/Incorrect input data
    - External HTTP server throws a 400 level error

    """
    pass


class ServerException(Exception):
    """
    An Exception which marks an error made by an external server.

    Some examples of when to use this are:
    - External server throws a 500 Error

    """
    pass


class LoggedException(Exception):

    def __init__(self, ex, output):
        super(LoggedException, self).__init__(ex)
        self.output = output
