from traits.api import (
    Button, Dict, HasTraits, Int, List, Tuple, Unicode,
    provides
)

from force_wfmanager.i_contributed_ui import IContributedUI


@provides(IContributedUI)
class ContributedUI(HasTraits):
    """An object which contains a custom UI for a particular workflow file."""

    #: Name for the UI in selection screen
    name = Unicode()

    #: Description of the UI
    desc = Unicode()

    #: List of plugin ids and versions required for this UI
    required_plugins = List(Tuple(Unicode, Int))

    #: The path to a template workflow file
    workflow_file = Unicode()

    #: A map from (workflow element uuid, attribute name) to
    #: (ui display name)
    # TODO: Consider allowing this information to be saved to/loaded from a workflow file
    #       which would allow a user to make minor modifications to a mostly fixed workflow
    workflow_map = Dict()

    # A button to
    run_button = Button("Run Workflow")
