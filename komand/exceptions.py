# -*- coding: utf-8 -*-
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


class ConnectionTestException(Exception):
    """
    An Exception which marks an error that occurred during a connection test.

    This Exception provides a method for consistent and well-handled error messaging.
    """

    class Preset(object):
        """
        Constants available for use as preset arguments to the initializer
        """
        API_KEY = "api_key"
        UNAUTHORIZED = "unauthorized"
        RATE_LIMIT = "rate_limit"
        USERNAME_PASSWORD = "username_password"
        NOT_FOUND = "not_found"
        SERVER_ERROR = "server_error"
        SERVICE_UNAVAILABLE = "service_unavailable"

    # Dictionary of cause messages
    causes = {
        Preset.API_KEY: "Invalid API key provided.",
        Preset.UNAUTHORIZED: "The account configured in your plugin connection is unauthorized to access this service.",
        Preset.RATE_LIMIT: "The account configured in your plugin connection is currently rate-limited.",
        Preset.USERNAME_PASSWORD: "Invalid username or password provided.",
        Preset.NOT_FOUND: "Invalid or unreachable endpoint provided.",
        Preset.SERVER_ERROR: "Server error occurred",
        Preset.SERVICE_UNAVAILABLE: "The service this plugin is designed for is currently unavailable."
    }

    # Dictionary of assistance/remediation messages
    assistances = {
        Preset.API_KEY: "Verify your API key configured in your connection is correct.",
        Preset.UNAUTHORIZED: "Verify the permissions for your account and try again.",
        Preset.RATE_LIMIT: "Adjust the time between requests in the plugin action configuration if possible or "
                           "consider adding a Sleep plugin step between attempts.",
        Preset.USERNAME_PASSWORD: "Verify your username and password are correct.",
        Preset.NOT_FOUND: "Verify the endpoint/URL/hostname configured in your plugin connection is correct.",
        Preset.SERVER_ERROR: "Verify your plugin connection inputs are correct and not malformed and try again. "
                             "If the issue persists, please contact support.",
        Preset.SERVICE_UNAVAILABLE: "Try again later. If the issue persists, please contact support."
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
            self.cause = cause if cause else ""
            self.assistance = assistance if assistance else ""

    def __str__(self):
        return "Connection test failed! {cause} {assistance}".format(cause=self.cause,
                                                                     assistance=self.assistance)
