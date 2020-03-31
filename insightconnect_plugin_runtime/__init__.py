# -*- coding: utf-8 -*-
import insightconnect_plugin_runtime.action
import insightconnect_plugin_runtime.cli
import insightconnect_plugin_runtime.connection
import insightconnect_plugin_runtime.plugin
import insightconnect_plugin_runtime.schema
import insightconnect_plugin_runtime.trigger
import insightconnect_plugin_runtime.variables
import insightconnect_plugin_runtime.helper
import insightconnect_plugin_runtime.dispatcher
import insightconnect_plugin_runtime.exceptions
import certifi
import os
import logging

Plugin = insightconnect_plugin_runtime.plugin.Plugin
Action = insightconnect_plugin_runtime.action.Action
Trigger = insightconnect_plugin_runtime.trigger.Trigger
Connection = insightconnect_plugin_runtime.connection.Connection
Input = insightconnect_plugin_runtime.variables.Input
Output = insightconnect_plugin_runtime.variables.Output
CLI = insightconnect_plugin_runtime.cli.CLI

# Many plugins use the certifi package, particularly indirectly through
# the requests package. Certifi can be monkey-patched to not use the
# dedicated CA bundle, which is exactly what we will do. In fact, the
# requests package even suggests to do exactly this:
# https://github.com/requests/requests/blob/master/requests/certs.py
# http://docs.python-requests.org/en/master/user/advanced/#ca-certificates
# So, we'll ask it to use SSL_CERT_FILE, one of the most common env vars
# that would contain a path to SSL CA certificate bundle.
# We'll also set REQUESTS_CA_BUNDLE if it wasn't set already.

old_certifi_value = certifi.where()


def where():
    try:
        env_var = os.environ["SSL_CERT_FILE"]
        if len(env_var) > 0 and os.path.exists(env_var):
            # tell the requests package to use it too
            os.environ["REQUESTS_CA_BUNDLE"] = env_var
            # and return callers of certifi.where() a shiny custom path
            # to do their own verifications against the bundle.
            return env_var
        else:
            # old certifi value
            return old_certifi_value
    except Exception as ex:
        # old certifi value
        return old_certifi_value


# and here's the monkey-patch itself.
certifi.where = where

root_logger = logging.getLogger()
root_logger.setLevel("DEBUG")
root_logger.addHandler(logging.StreamHandler())
