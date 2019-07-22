from envisage.plugin import Plugin
from pyface.api import ImageResource

from traits.api import (
    HasTraits, List, Unicode
)
from traitsui.api import (
    ImageEditor, View, Group, HGroup, UItem, ListStrEditor, VGroup, Spring,
    TextEditor, UReadonly
)

# VerifierError severity constants
_ERROR = "error"
_WARNING = "warning"
_INFO = "information"


# Item positioning shortcuts
def horizontal_centre(item_or_group):
    return HGroup(Spring(), item_or_group, Spring())


class WorkflowInfo(HasTraits):

    # -------------------
    # Required Attributes
    # -------------------

    #: Filename for the current workflow (if any)
    workflow_filename = Unicode()

    #: A list of the loaded plugins
    plugins = List(Plugin)

    #: The factory currently selected in the SetupPane
    selected_factory_name = Unicode()

    #: An error message for the entire workflow
    error_message = Unicode()

    # ---------------------
    # Dependent Attributes
    # ---------------------

    #: The force project logo! Stored at images/Force_Logo.png
    image = ImageResource('Force_Logo.png')

    #: Message indicating currently loaded file
    workflow_filename_message = Unicode()

    #: A list of plugin names
    plugin_names = List(Unicode)

    # -----------
    #    View
    # -----------

    traits_view = View(
        VGroup(
            horizontal_centre(
                Group(
                    UItem('image',
                          editor=ImageEditor(scale=True,
                                             allow_upscaling=False,
                                             preserve_aspect_ratio=True)),
                    visible_when="selected_factory == 'Workflow'"
                )
            ),
            Group(
                UReadonly('plugin_names',
                          editor=ListStrEditor(editable=False)),
                show_border=True,
                label='Available Plugins',
                visible_when="selected_factory not in ['KPI']"
            ),
            Group(
                UReadonly('workflow_filename_message', editor=TextEditor()),
                show_border=True,
                label='Workflow Filename',
            ),
            Group(
                UReadonly('error_message', editor=TextEditor()),
                show_border=True,
                label='Workflow Errors',
                visible_when="selected_factory_name == 'Workflow'"
            ),

        )
    )

    # -------------------
    #      Defaults
    # -------------------

    def _plugin_names_default(self):
        return [plugin.name for plugin in self.plugins]

    def _workflow_filename_message_default(self):
        if self.workflow_filename == '':
            return 'No File Loaded'
        return 'Current File: ' + self.workflow_filename
