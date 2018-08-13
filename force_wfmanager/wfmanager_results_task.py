import logging

from envisage.ui.tasks.tasks_application import TasksApplication

from pyface.tasks.action.api import SMenuBar
from pyface.tasks.api import Task, TaskLayout, PaneItem

from traits.api import Instance

from force_wfmanager.central_pane.graph_pane import GraphPane
from force_wfmanager.left_side_pane.results_pane import ResultsPane

log = logging.getLogger(__name__)


class WfManagerResultsTask(Task):
    id = 'force_wfmanager.wfmanager_results_task'
    name = 'Workflow Manager (Results)'

    #: Side Pane containing the tree editor for the Workflow and the Run button
    side_pane = Instance(ResultsPane)

    #: The application associated with this Task
    app = Instance(TasksApplication)

    #: The menu bar for this task.
    menu_bar = Instance(SMenuBar)

    def __init__(self, shared_menu_bar):
        self.menu_bar = shared_menu_bar
        super(WfManagerResultsTask, self).__init__()

    # TODO: Add a nice looking toolbar

    def create_central_pane(self):
        """ Creates the central pane which contains the analysis part
        (pareto front and output KPI values)
        """
        print(self.app.analysis_m)
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
