from traits.api import (
    Button, Dict, HasTraits, Int, List, Tuple, Unicode, on_trait_change,
    provides
)

from force_wfmanager.i_contributed_ui import IContributedUI


@provides(IContributedUI)
class ContributedUI(HasTraits):
    """An object which contains a custom UI and workflow for a plugin"""

    #: Name for the UI in selection screen
    name = Unicode()

    #: Description of the UI
    desc = Unicode()

    #: List of plugin ids and versions required for this UI
    required_plugins = List(Tuple(Unicode, Int))

    #; The path to a template workflow file
    workflow_file = Unicode()

    #: A map from (workflow element uuid, attribute name) to
    #: (ui display name)
    workflow_map = Dict()

    run_button = Button("Run Workflow")
