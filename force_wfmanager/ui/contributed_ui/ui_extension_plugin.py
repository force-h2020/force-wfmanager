from traits.api import List

from force_bdss.api import BaseExtensionPlugin
from force_wfmanager.ui.contributed_ui.i_contributed_ui import IContributedUI


class UIExtensionPlugin(BaseExtensionPlugin):
    """A plugin which also contributes one or more custom UIs"""
    contributed_UIs = List(
        IContributedUI, contributes_to='plugin_ui'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contributed_UIs = self.get_contributed_UIs()

    def get_contributed_UIs(self):
        """Returns a list of custom UIs contributed by this plugin"""
        raise NotImplementedError(
            f"The function 'get_contributed_UIs' must be implemented in the "
            f"{self.__class__.__name__} class"
        )
