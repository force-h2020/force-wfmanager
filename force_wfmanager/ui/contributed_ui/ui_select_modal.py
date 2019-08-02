from traits.api import (
    Dict, Enum, HasRequiredTraits, Instance, List, Unicode, on_trait_change
)
from traitsui.api import (
    Handler, HGroup, Item, OKCancelButtons, Spring, TextEditor, UReadonly,
    View, VGroup
)

from force_bdss.api import BaseExtensionPlugin
from force_wfmanager.ui.contributed_ui.contributed_ui import ContributedUI


class UISelectHandler(Handler):
    """A Handler to provide correct closing behaviour for UISelectModal.
    If the OK button is pressed, open a window with the view for that UI.
    """
    def close(self, info, is_ok):
        if not is_ok:
            info.object.selected_ui = None
        return True


class UISelectModal(HasRequiredTraits):

    #: A list of contributed UIs received from plugins
    contributed_uis = List(ContributedUI, required=True)

    #: A list of available plugins
    available_plugins = List(Instance(BaseExtensionPlugin), required=True)

    #: A dictionary of plugin names and versions, generated from
    #: available_plugins
    avail_plugin_info = Dict()

    #: Mapping allowing selection of a UI by its name
    ui_name_map = Dict(Unicode, Instance(ContributedUI))

    #: The name of the currently selected UI
    selected_ui_name = Enum(Unicode, values='_contributed_ui_names')

    #: List of discovered ContributedUI names
    _contributed_ui_names = List(Unicode)

    #: The currently selected UI
    selected_ui = Instance(ContributedUI)

    #: The description for the currently selected UI
    selected_ui_desc = Unicode()

    traits_view = View(VGroup(
        HGroup(
            Spring(),
            Item("selected_ui_name", label="Selected UI "),
            Spring()
        ),
        HGroup(
            UReadonly(
                "selected_ui_desc", editor=TextEditor(),
                visible_when="selected_ui is not None"
            )
        ),
    ),
        buttons=OKCancelButtons,
        handler=UISelectHandler(),
        kind="livemodal",
        resizable=True,
        title="Select Custom UI",
        width=600,
    )

    def __contributed_ui_names_default(self):
        return [''] + [ui.name for ui in self.contributed_uis
                       if self._check_ui_plugins_available(ui)]

    @on_trait_change("selected_ui_name")
    def select_ui(self):
        """Set :attr:`selected_ui` and update :attr:`selected_ui_desc` when the
        user selects a UI from the available UIs combobox."""
        if not self.selected_ui_name:
            self.selected_ui = None
        else:
            self.selected_ui = self.ui_name_map[self.selected_ui_name]
            self.selected_ui_desc = DESCRIPTION_TEMPLATE.format(
                self.selected_ui.name, self.selected_ui.desc
            )

    def _ui_name_map_default(self):
        """Convenience mapping from user friendly UI names to the
        ContributedUI object itself
        """
        return {ui.name: ui for ui in self.contributed_uis}

    def _avail_plugin_info_default(self):
        return {
            plugin.id: plugin.version for plugin in self.available_plugins
        }

    def _check_ui_plugins_available(self, ui):
        """Check that all plugins required by a ContributedUI are present.

        Parameters
        ----------
        ui: ContributedUI
            The ContributedUI to be checked.
        """
        for plugin_name, plugin_ver in ui.required_plugins.items():
            # Check if the plugin has been loaded and that the version number
            # is greater or equal to the minimum version required.
            if self.avail_plugin_info.get(plugin_name, -1) < plugin_ver:
                return False
        return True


DESCRIPTION_TEMPLATE = """
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style type="text/css">
            .container{{
                width: 100%;
                font-family: sans-serif;
                display: block;
            }}
        </style>
    </head>
    <body>
        <h2>{}</h2>
        <p>{}</p>
    </body>
    </html>
"""
