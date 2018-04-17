# -*- coding: utf-8 -*-
import komand.action
import komand.cli
import komand.connection
import komand.plugin
import komand.trigger
import komand.variables
import komand.helper
import komand.dispatcher
import certifi
import os

Plugin = komand.plugin.Plugin
Action = komand.action.Action
Trigger = komand.trigger.Trigger
Connection = komand.connection.Connection
Input = komand.variables.Input
Output = komand.variables.Output
CLI = komand.cli.CLI


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
        env_var = os.environ['SSL_CERT_FILE']
        if len(env_var) > 0 and os.path.exists(env_var):
            # tell the requests package to use it too
            os.environ['REQUESTS_CA_BUNDLE'] = env_var
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
