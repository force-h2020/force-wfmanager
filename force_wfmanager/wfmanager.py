from pyface.tasks.api import Task, TaskLayout, PaneItem
from force_wfmanager.central_pane.central_pane import CentralPane
from force_wfmanager.left_side_pane.workflow_settings import WorkflowSettings


class WfManager(Task):
    id = 'wfmanager.wfmanager'
    name = 'Workflow Manager'

    def create_central_pane(self):
        """ Creates the central pane which contains the analysis and
        configuration panes
        """
        return CentralPane()

    def create_dock_panes(self):
        """ Creates the dock panes which contains the MCO, KPIs and Constraints
        management """
        workflow_settings = WorkflowSettings()
        return [workflow_settings]

    def _default_layout_default(self):
        """ Defines the default layout of the task window """
        return TaskLayout(
            left=PaneItem('wfmanager.workflow_settings')
        )
