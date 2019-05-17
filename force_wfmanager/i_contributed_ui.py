from traits.api import Dict, List, Tuple, Unicode, Int, Interface
from traitsui.api import View

class IContributedUI(Interface):

    #: Name
    name = Unicode()

    #: Description of UI
    desc = Unicode()

    #: List of plugin ids and versions required for this UI
    required_plugins = List(Tuple(Unicode, Int))

    # ; The path to a template workflow file
    workflow_file = Unicode()

    #: A map from (workflow element uuid, attribute name) to
    #: (ui name, ui value)
    workflow_map = Dict()

    #: A TraitsUI view for the workflow model
    workflow_view = View()