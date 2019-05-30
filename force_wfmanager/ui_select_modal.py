from collections import Iterable
import copy
import json
from traits.api import (
    Button, Dict, Enum, HasRequiredTraits, Instance, List, Unicode,
    on_trait_change
)
from traitsui.api import (
    Handler, HGroup, Item, OKCancelButtons, Spring, TextEditor, View, VGroup,
    UItem, UReadonly
)
from pyface.api import FileDialog, OK, error

from force_bdss.api import BaseExtensionPlugin
from force_wfmanager.contributed_ui import ContributedUI


class UISelectHandler(Handler):
    """A Handler to provide correct closing behaviour for UISelectModal."""
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
    #: available_plugins`
    _avail_plugin_info = Dict()

    #: Mapping allowing selection of a UI by its name
    ui_name_map = Dict(Unicode, Instance(ContributedUI))

    #: The name of the currently seleted UI
    selected_ui_name = Enum(Unicode, values='_contributed_ui_names')

    #: List of discovered ContributedUI names
    _contributed_ui_names = List(Unicode)

    #: The currently selected UI
    selected_ui = Instance(ContributedUI)

    #: The description for the currently selected UI
    selected_ui_desc = Unicode()

    #: The path of the currently selected workflow file
    selected_ui_workflow_file = Unicode()

    #: Opens an alternative workflow file (Provided the UI contents can also
    #: be mapped to items in the workflow)
    open_workflow_file = Button("Open alternative workflow file..")

    traits_view = View(VGroup(
        HGroup(
            Spring(),
            Item("selected_ui_name", label="Selected UI "),
            Spring()
        ),
        HGroup(
            Item(
                "selected_ui_workflow_file", label="Workflow File",
            ),
            UItem("open_workflow_file"),
            visible_when="selected_ui is not None",
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
        """Set selected_ui and update description shown in the UI."""
        if not self.selected_ui_name:
            self.selected_ui = None
        else:
            self.selected_ui = self.ui_name_map[self.selected_ui_name]
            self.selected_ui_desc = FORMATTED_DESCRIPTION.format(
                self.selected_ui.name, self.selected_ui.desc
            )
            self.selected_ui_workflow_file = self.selected_ui.workflow_file

    def _ui_name_map_default(self):
        return {ui.name: ui for ui in self.contributed_uis}

    def __avail_plugin_info_default(self):
        return {
            plugin.name: plugin.version for plugin in self.available_plugins
        }

    def _check_ui_plugins_available(self, ui):
        """Check that any additional plugins required by the contributed UI
        are present

        Parameters
        ----------
        ui: ContributedUI
            The ContributedUI to be checked.
        """
        for plugin_name, plugin_ver in ui.required_plugins:
            if self.avail_plugin_info.get(plugin_name, -1) < plugin_ver:
                return False
        return True

    @on_trait_change('selected_ui_workflow_file')
    def set_selected_ui_workflow_file(self):
        if self.selected_ui is not None:
            self.selected_ui.workflow_file = self.selected_ui_workflow_file

    @on_trait_change("open_workflow_file")
    def open_workflow(self):
        """ Shows a dialog to open a workflow file """
        dialog = FileDialog(
            action="open",
            wildcard='JSON files (*.json)|*.json|'
        )
        result = dialog.open()
        f_name = dialog.path
        if result is OK:
            with open(f_name, 'r') as f_reader:
                json_data = json.load(f_reader)
                missing_items = self._workflow_items_unavailable(json_data)
            if not missing_items:
                # Set workflow file in UI
                self.selected_ui_workflow_file = f_name
                # Set workflow file on ContributedUI object
                self.selected_ui.workflow_file = f_name
            else:
                error_message = (
                    "The workflow file '{wf_file}' did not contain items "
                    "specified in the 'workflow_map' of this ContributedUI. "
                    "Click 'show details' for further information.".format(
                        wf_file=f_name
                    )
                )
                missing_item_string = '\n'.join([
                    "Item with UUID: '{}' and attr: '{}'".format(uuid, attr)
                    for uuid, attr in missing_items.items()
                ])
                error_detail = (
                    'Not found in workflow file:\n' + missing_item_string
                )
                error(
                    parent=None, message=error_message,
                    title='Error loading workflow file', detail=error_detail
                )

    def _workflow_items_unavailable(self, json_data):
        """Checks if the items specified in the ContributedUI have a
        counterpart in the workflow file itself"""
        wf_map = copy.copy(self.selected_ui.workflow_map)
        wf_dict = json_data['workflow']
        _iters = (dict, list, tuple, set)

        def depth_search(iterable, workflow_map):
            # Check if the dict contains a matching uuid
            if isinstance(iterable, dict):
                for key, val in iterable.items():
                    if key == 'uuid':
                        workflow_item_uuid = iterable[key]
                        if (workflow_item_uuid in workflow_map and
                                workflow_map[val] in iterable.keys()):
                            wf_map.pop(workflow_item_uuid)
                    # Check any sub-iterables
                    if isinstance(val, _iters):
                        depth_search(val, workflow_map)
            # If we have a list, set or tuple, check if any of its elements
            # are iterables also.
            elif isinstance(iterable, Iterable):
                for val in iterable:
                    if isinstance(val, _iters):
                        depth_search(val, workflow_map)

        depth_search(wf_dict, self.selected_ui.workflow_map)
        return wf_map


FORMATTED_DESCRIPTION = """
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