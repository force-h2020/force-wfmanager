from traits.api import List

from pyface.tasks.api import Task, TaskLayout, PaneItem

from force_wfmanager.central_pane.central_pane import CentralPane
from force_wfmanager.left_side_pane.workflow_settings import WorkflowSettings


class WfManagerTask(Task):
    id = 'force_wfmanager.wfmanager_task'
    name = 'Workflow Manager'

    mco_bundles = List
    data_source_bundles = List
    kpi_calculator_bundles = List

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
            available_kpi_calculator_factories=self.kpi_calculator_bundles)
        return [workflow_settings]

    def _default_layout_default(self):
        """ Defines the default layout of the task window """
        return TaskLayout(
            left=PaneItem('force_wfmanager.workflow_settings')
        )
