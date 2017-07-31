from traits.api import List, Instance

from pyface.tasks.api import Task, TaskLayout, PaneItem
from pyface.tasks.action.api import SMenu, SMenuBar, TaskAction
from pyface.api import FileDialog, OK

from force_bdss.api import IMCOBundle, IDataSourceBundle, IKPICalculatorBundle
from force_bdss.workspecs.workflow import Workflow
from force_bdss.io.workflow_writer import WorkflowWriter
from force_bdss.io.workflow_reader import WorkflowReader

from force_wfmanager.central_pane.central_pane import CentralPane
from force_wfmanager.left_side_pane.workflow_settings import WorkflowSettings


class WfManagerTask(Task):
    id = 'force_wfmanager.wfmanager_task'
    name = 'Workflow Manager'

    workflow = Instance(Workflow)

    mco_bundles = List(Instance(IMCOBundle))
    data_source_bundles = List(Instance(IDataSourceBundle))
    kpi_calculator_bundles = List(Instance(IKPICalculatorBundle))

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
        workflow_settings = WorkflowSettings(
            available_mco_factories=self.mco_bundles,
            available_data_source_factories=self.data_source_bundles,
            available_kpi_calculator_factories=self.kpi_calculator_bundles,
            workflow_model=self.workflow)
        return [workflow_settings]

    def save_workflow(self):
        """ Shows a dialog to save the workflow into a JSON file """
        dialog = FileDialog(action="save as", default_filename="workflow.json")
        result = dialog.open()

        if result is OK:
            writer = WorkflowWriter()
            with open(dialog.path, 'wr') as output:
                writer.write(self.workflow, output)

    def load_workflow(self):
        """ Shows a dialog to load a workflow file """
        dialog = FileDialog(action="open")
        result = dialog.open()

        if result is OK:
            reader = WorkflowReader()
            with open(dialog.path, 'r') as fobj:
                self.workflow = reader.read(fobj)

    def _default_layout_default(self):
        """ Defines the default layout of the task window """
        return TaskLayout(
            left=PaneItem('force_wfmanager.workflow_settings')
        )

    def _workflow_default(self):
        return Workflow()
