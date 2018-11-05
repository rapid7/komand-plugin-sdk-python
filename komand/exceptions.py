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
    """
    An Exception which holds the step output dictionary.
    """

    def __init__(self, ex, output):
        super(LoggedException, self).__init__(ex)
        self.ex = ex
        self.output = output


class ConnectionTestException(BaseException):
    """
    An Exception which marks an error that occurred during a connection test.

    This Exception provides a method for consistent and well-handled error messaging.
    """

    class Preset(object):
        API_KEY = "api_key"
        UNAUTHORIZED = "unauthorized"
        RATE_LIMIT = "rate_limit"

    causes = {
        Preset.API_KEY: "Invalid API key used.",
        Preset.UNAUTHORIZED: "The account configured in your plugin connection is unauthorized to access this service.",
        Preset.RATE_LIMIT: "The account configured in your plugin connection is currently rate-limited.",
    }

    assistances = {
        Preset.API_KEY: "Verify your API key configured in your connection is correct.",
        Preset.UNAUTHORIZED: "Verify the permissions for your account and try again.",
        Preset.RATE_LIMIT: "Adjust the time between requests in the plugin action configuration if possible or "
                           "consider adding a Sleep plugin step between attempts.",
    }

    def __init__(self, cause=None, assistance=None, preset=None):
        """
        Initializes a new ConnectionTestException. User must supply all punctuation/grammar.
        :param cause: Cause of the error. Leave empty if using preset.
        :param assistance: Possible remediation steps for the error. Leave empty if using preset.
        :param preset: Preset error and remediation steps to use.
        """
        
        if preset:
            self.cause, self.assistance = self.causes[preset], self.assistances[preset]
        else:
            self.cause = cause
            self.assistance = assistance

    def __str__(self):
        return "Connection test failed! {cause} {assistance}".format(cause=self.cause,
                                                                     assistance=self.assistance)
