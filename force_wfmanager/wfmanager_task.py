from traits.api import Instance, on_trait_change

from pyface.tasks.api import Task, TaskLayout, PaneItem
from pyface.tasks.action.api import SMenu, SMenuBar, TaskAction
from pyface.api import FileDialog, OK, error

from force_bdss.bundle_registry_plugin import BundleRegistryPlugin
from force_bdss.core.workflow import Workflow
from force_bdss.io.workflow_writer import WorkflowWriter
from force_bdss.io.workflow_reader import WorkflowReader, InvalidFileException

from force_wfmanager.central_pane.central_pane import CentralPane
from force_wfmanager.left_side_pane.workflow_settings import WorkflowSettings


class WfManagerTask(Task):
    id = 'force_wfmanager.wfmanager_task'
    name = 'Workflow Manager'

    #: Workflow model
    workflow_m = Instance(Workflow, allow_none=False)

    #: WorkflowSettings pane, it displays the workflow in a tree editor and
    #: allows to edit it
    workflow_settings = Instance(WorkflowSettings, allow_none=False)

    #: Registry of the available bundles
    bundle_registry = Instance(BundleRegistryPlugin)

    #: Menu bar on top of the GUI
    menu_bar = SMenuBar(SMenu(
        TaskAction(
            name='Save Workflow...',
            method='save_workflow',
            accelerator='Ctrl+S',
        ),
        TaskAction(
            name='Load Workflow...',
            method='load_workflow',
            accelerator='Ctrl+O',
        ), id='File', name='&File'
    ))

    def create_central_pane(self):
        """ Creates the central pane which contains the analysis part
        (pareto front and output KPI values)
        """
        return CentralPane()

    def create_dock_panes(self):
        """ Creates the dock panes which contains the MCO, datasources and
        Constraints management """
        return [self.workflow_settings]

    def save_workflow(self):
        """ Shows a dialog to save the workflow into a JSON file """
        dialog = FileDialog(action="save as", default_filename="workflow.json")
        result = dialog.open()

        if result is OK:
            writer = WorkflowWriter()
            with open(dialog.path, 'wr') as output:
                writer.write(self.workflow_m, output)

    def load_workflow(self):
        """ Shows a dialog to load a workflow file """
        dialog = FileDialog(action="open")
        result = dialog.open()

        if result is OK:
            reader = WorkflowReader(self.bundle_registry)
            try:
                with open(dialog.path, 'r') as fobj:
                    self.workflow_m = reader.read(fobj)
            except InvalidFileException as e:
                error(
                    None,
                    'Cannot read the requested file:\n\n{}'.format(
                        str(e)),
                    'Error when reading file'
                )

    def _default_layout_default(self):
        """ Defines the default layout of the task window """
        return TaskLayout(
            left=PaneItem('force_wfmanager.workflow_settings')
        )

    def _workflow_m_default(self):
        return Workflow()

    def _workflow_settings_default(self):
        registry = self.bundle_registry
        return WorkflowSettings(
            available_mco_factories=registry.mco_bundles,
            available_data_source_factories=registry.data_source_bundles,
            available_kpi_calculator_factories=registry.kpi_calculator_bundles,
            workflow_m=self.workflow_m)

    @on_trait_change('workflow_m')
    def update_workflow_settings(self):
        self.workflow_settings.workflow_m = self.workflow_m
