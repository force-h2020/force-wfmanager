import logging

from envisage.ui.tasks.tasks_application import TasksApplication

from pyface.tasks.action.api import SMenuBar, SMenu, TaskAction
from pyface.tasks.api import Task, TaskLayout, PaneItem

from traits.api import Instance

from force_wfmanager.central_pane.graph_pane import GraphPane
from force_wfmanager.left_side_pane.results_pane import ResultsPane
from force_wfmanager.TaskToggleGroupAccelerator import (
    TaskToggleGroupAccelerator
)

log = logging.getLogger(__name__)


class WfManagerResultsTask(Task):
    id = 'force_wfmanager.wfmanager_results_task'
    name = 'Results'

    #: Side Pane containing the tree editor for the Workflow and the Run button
    side_pane = Instance(ResultsPane)

    #: The application (Wfmanager) associated with this Task. Accessible here
    #: because of the way envisage applications work
    app = Instance(TasksApplication)

    #: The menu bar for this task.
    menu_bar = Instance(SMenuBar)

    # TODO: Add a nice looking toolbar

    def _menu_bar_default(self):
        """A menu bar with elements shared between the different tasks.
        Elements unique to a specific task are added when the task is
        instantiated. Functions associated to the shared methods are located
        at the application level."""
        menu_bar = SMenuBar(
            SMenu(
                TaskAction(
                    name='Exit',
                    method='app.exit',
                    accelerator='Ctrl+Q',
                ),
                name='&Workflow Manager'
            ),
            SMenu(
                TaskAction(
                    name='Open Workflow...',
                    method='app.open_workflow',
                    enabled_name='app.save_load_enabled',
                    accelerator='Ctrl+O',
                ),
                TaskAction(
                    name='Save Workflow',
                    method='app.save_workflow',
                    enabled_name='app.save_load_enabled',
                    accelerator='Ctrl+S',
                ),
                TaskAction(
                    name='Save Workflow as...',
                    method='app.save_workflow_as',
                    enabled_name='app.save_load_enabled',
                    accelerator='Shift+Ctrl+S',
                ),
                TaskAction(
                    name='Plugins...',
                    method='app.open_plugins'
                ),
                name='&File'
            ),
            SMenu(
                TaskAction(
                    name='About WorkflowManager...',
                    method='app.open_about'
                ),
                name='&Help'
            ),
            SMenu(TaskToggleGroupAccelerator(), id='View', name='&View')
        )
        return menu_bar

    def create_central_pane(self):
        """ Creates the central pane which contains the analysis part
        (pareto front and output KPI values)
        """
        return GraphPane(self.app.analysis_m)

    def create_dock_panes(self):
        """ Creates the dock panes """
        return [self.side_pane]

    def _side_pane_default(self):
        return ResultsPane(
            analysis_model=self.app.analysis_m
        )

    def _default_layout_default(self):
        """ Defines the default layout of the task window """
        return TaskLayout(
            left=PaneItem('force_wfmanager.results_pane'),
        )

    def _app_default(self):
        return self.window.application
