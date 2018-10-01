from envisage.plugin import Plugin
from force_wfmanager.left_side_pane.variable_names_registry import \
    VariableNamesRegistry
from force_wfmanager.left_side_pane.workflow_model_view import \
    WorkflowModelView
from pyface.api import ImageResource
from traits.api import HasTraits, List, Instance, Unicode, Tuple
from traits.traits import Property
from traitsui.api import (
    ImageEditor, View, Group, UItem, ListStrEditor, VGroup
)
from traitsui.editors import TableEditor, TextEditor
from traitsui.item import UReadonly
from traitsui.table_column import ObjectColumn


class TableRow(HasTraits):

    type = Unicode()

    name = Unicode()


class WorkflowInfo(HasTraits):

    image = ImageResource('Force_Logo.png')

    non_kpi_variables = List(Tuple(Unicode, Unicode))

    non_kpi_variables_rep = List(TableRow)

    kpi_names = List(Unicode)

    plugins = List(Plugin)

    plugin_names = List(Unicode)

    variable_names_registry = Instance(VariableNamesRegistry)

    workflow_mv = Instance(WorkflowModelView)

    workflow_filename = Unicode()

    workflow_filename_message = Unicode()

    table_edit = TableEditor(
        columns=[
            ObjectColumn(name="name", label="name", resize_mode="stretch"),
            ObjectColumn(name="type", label="type", resize_mode="stretch")
        ],
        auto_size=False,
    )

    traits_view = View(
        VGroup(
            Group(
                UReadonly('plugin_names', editor=ListStrEditor()),
                show_border=True,
                label='Available Plugins'
            ),
            Group(
                UReadonly('non_kpi_variables_rep', editor=table_edit),
                show_border=True,
                label='Non-KPI Variables'
            ),
            Group(
                UItem('workflow_filename_message', editor=TextEditor()),
                style='custom',
                show_border=True,
                label='Workflow Filename',
            ),
            Group(
                UItem('image', editor=ImageEditor())
            )
        )
    )

    def _plugin_names_default(self):
        return [plugin.name for plugin in self.plugins]

    def _non_kpi_variables_rep_default(self):
        non_kpi = []
        if self.variable_names_registry is None:
            return non_kpi
        for exec_layer in self.variable_names_registry.available_variables_stack:
            for variable in exec_layer:
                if variable[0] not in self.kpi_names:
                    rep = TableRow(name=variable[0], type=variable[1])
                    non_kpi.append(rep)
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
