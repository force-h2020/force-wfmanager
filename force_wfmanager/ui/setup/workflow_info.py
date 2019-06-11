from envisage.plugin import Plugin

from pyface.api import ImageResource
from traits.api import HasTraits, List, Instance, Unicode
from traitsui.api import (
    ImageEditor, View, Group, HGroup, UItem, ListStrEditor, VGroup, Spring,
    TableEditor, TextEditor, UReadonly, ObjectColumn
)

from force_wfmanager.utils.variable_names_registry import \
    VariableNamesRegistry
from force_wfmanager.ui.setup.model_views.workflow_model_view import \
    WorkflowModelView

# Item positioning shortcuts


def horizontal_centre(item_or_group):
    return HGroup(Spring(), item_or_group, Spring())


class TableRow(HasTraits):
    """A representation of a variable in the workflow. Instances of TableRow
    are displayed in a table using the TableEditor."""

    #: The variable's type
    type = Unicode()

    #: The variable's name
    name = Unicode()


class WorkflowInfo(HasTraits):
    """A view containing information on certain aspects of the workflow
    state. This includes: Current errors, Available variables, Plugins loaded
    and the current workflow filename."""

    # -------------------
    # Required Attributes
    # -------------------

    #: A list of the loaded plugins
    plugins = List(Plugin)

    #: The factory currently selected in the SetupPane
    selected_factory = Unicode()

    #: The top-level workflow modelview
    workflow_mv = Instance(WorkflowModelView)

    #: Filename for the current workflow (if any)
    workflow_filename = Unicode()

    # ------------------
    # Regular Attributes
    # ------------------

    #: An error message for the entire workflow
    error_message = Unicode()

    #: The force project logo! Stored at images/Force_Logo.png
    image = ImageResource('Force_Logo.png')

    #: A list of TableRow instances, each representing a variable
    non_kpi_variables_rep = List(TableRow)

    #: The names of the KPIs in the Workflow
    kpi_names = List(Unicode)

    #: A list of plugin names
    plugin_names = List(Unicode)

    #: Data structure containing current variable names
    variable_names_registry = Instance(VariableNamesRegistry)

    #: Message indicating currently loaded file
    workflow_filename_message = Unicode()

    # ----
    # View
    # ----

    table_edit = TableEditor(
        columns=[
            ObjectColumn(name="name", label="name", resize_mode="stretch"),
            ObjectColumn(name="type", label="type", resize_mode="stretch")
        ],
        auto_size=False,
    )

    traits_view = View(
        VGroup(
            horizontal_centre(
                UItem('image', editor=ImageEditor(scale=True,
                                                  allow_upscaling=False,
                                                  preserve_aspect_ratio=True))
            ),
            Group(
                UReadonly('plugin_names',
                          editor=ListStrEditor(editable=False)),
                show_border=True,
                label='Available Plugins',
                visible_when="selected_factory not in ['KPI']"
            ),
            Group(
                UReadonly('non_kpi_variables_rep', editor=table_edit),
                show_border=True,
                label='Non-KPI Variables',
                visible_when="selected_factory == 'KPI'"
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
                visible_when="selected_factory == 'Workflow'"
            ),

        )
    )

    # Defaults

    def _plugin_names_default(self):
        return [plugin.name for plugin in self.plugins]

    def _non_kpi_variables_rep_default(self):
        non_kpi = []
        if self.variable_names_registry is None:
            return non_kpi
        var_stack = self.variable_names_registry.available_variables_stack
        for exec_layer in var_stack:
            for variable in exec_layer:
                if variable[0] not in self.kpi_names:
                    variable_rep = TableRow(name=variable[0], type=variable[1])
                    non_kpi.append(variable_rep)
        return non_kpi

    def _variable_names_registry_default(self):
        return self.workflow_mv.variable_names_registry

    def _kpi_names_default(self):
        kpi_names = []
        if self.workflow_mv.mco_mv is None:
            return kpi_names
        for mco in self.workflow_mv.mco_mv:
            for kpi in mco.kpis_mv:
                kpi_names.append(kpi.name)
        return kpi_names

    def _workflow_filename_message_default(self):
        if self.workflow_filename == '':
            return 'No File Loaded'
        return 'Current File: ' + self.workflow_filename

    def _error_message_default(self):
        if self.workflow_mv.error_message == '':
            return ERROR_TEMPLATE.format(
                "No errors for current workflow", "")
        else:
            error_list = self.workflow_mv.error_message.split('\n')
            body_strings = ''.join([SINGLE_ERROR.format(error)
                                    for error in error_list])
            return ERROR_TEMPLATE.format(
                "Errors for current workflow:", body_strings)


ERROR_TEMPLATE = """
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
    <h4>{}</h4>
        {}
    </body>
    </html>
"""

SINGLE_ERROR = """<p>{}<\p>"""
