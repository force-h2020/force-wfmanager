from envisage.api import ServiceOffer
from traits.api import Instance, List

from force_bdss.api import BaseExtensionPlugin
from force_wfmanager.ui.contributed_ui.i_contributed_ui import IContributedUI


class UIExtensionPlugin(BaseExtensionPlugin):
    """A plugin which also contributes one or more custom UIs"""

    #: Service offers provided by this plugin.
    service_offers = List(
        Instance(ServiceOffer),
        contributes_to='envisage.service_offers',
    )

    def get_contributed_uis(self):
        """A method returning a list of ContributedUI subclasses provided by
        this plugin

        Example
        -------
        For a plugin which wants to offer the ContributedUIs: `ExperimentUI`
        and `AnalysisUI`, `get_contributed_uis` would be implemented as below

        >>> def get_contributed_uis(self):
        ...     return [
        ...         ExperimentUI, AnalysisUI
        ...     ]

        Where both `ExperimentUI` and `AnalysisUI` are subclasses of
        `ContributedUI`
        """
        raise NotImplementedError

    def _service_offers_default(self):
        contributed_ui_classes = self.get_contributed_uis()
        contributed_ui_offers = [
            ServiceOffer(protocol=IContributedUI, factory=factory)
            for factory in contributed_ui_classes
        ]
        return contributed_ui_offers
