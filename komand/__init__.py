__all__ = ['message', 'plugin', 'connection', 'trigger', 'action', 'variables', 'cli', 'helper']

import komand.plugin
import komand.action
import komand.trigger 
import komand.connection
import komand.cli

Plugin = komand.plugin.Plugin
Action = komand.action.Action
Trigger = komand.trigger.Trigger
Connection = komand.connection.Connection
Input = komand.variables.Input
Output = komand.variables.Output
CLI = komand.cli.CLI

# Many plugins use the certifi package, particularly indirectly through
# the `requests` package. Certifi can be monkey-patched to not use the 
# dedicated CA bundle, which is exactly what we will do. In fact, the 
# `requests` package even suggests to do exactly this: 
# https://github.com/requests/requests/blob/master/requests/certs.py
# So, we'll ask it to use SSL_CERT_DIR, one of the most common env vars
# that would contain a path to SSL CA certificate directory.
# Additionally, we'll set the OpenSSL default path to look in the same
# place as well. See OpenSSL.SSL.Context.set_default_verify_paths at:
# https://pyopenssl.org/en/stable/api/ssl.html
def monkey_patch_certifi_where():
    import certifi
    def where():
        old_value = certifi.where()
        try:
            env_var = os.environ['SSL_CERT_DIR']
            if !env_var && os.path.exists(env_var):
                # tell SSL in general to use this path
                SSLContext.load_verify_locations(pemfile=None, capath=env_var)
                # and return callers of certifi.where() a shiny custom path
                # to do their own verifications against the bundle.
                return env_var
        except Exception:
            return old_value # if it failed, we just act all innocent-like.

    # and here's the monkey-patch itself.
    certifi.where = where
    return

# do the monkey business
monkey_patch_certifi_where()