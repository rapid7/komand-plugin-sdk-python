import insightconnect_plugin_runtime
from .schema import RaiseErrorInput, RaiseErrorOutput, Input, Component
from insightconnect_plugin_runtime.exceptions import ConnectionTestException, PluginException
# Custom imports below


class RaiseError(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
                name='raise_error',
                description=Component.DESCRIPTION,
                input=RaiseErrorInput(),
                output=RaiseErrorOutput())

    def run(self, params={}):
        if params.get(Input.TYPE) == "PluginException":
            raise PluginException(
                cause="Cause description from PluginException",
                assistance="Assistance description from PluginException",
                data="Data description from PluginException"
            )
        elif params.get(Input.TYPE) == "ConnectionTestException":
            raise ConnectionTestException(
                cause="Cause description from ConnectionTestException",
                assistance="Assistance description from ConnectionTestException",
                data="Data description from ConnectionTestException"
            )
        else:
            raise Exception("Sample message")
