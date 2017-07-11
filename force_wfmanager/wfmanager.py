from pyface.tasks.api import Task, TaskLayout, PaneItem
from central_pane import CentralPane
from plugin_manager import PluginManager


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
        management
        """
        plugin_manager = PluginManager()
        return [plugin_manager]

    def _default_layout_default(self):
        """ Defines the default layout of the task window
        """
        return TaskLayout(
            left=PaneItem('wfmanager.plugin_manager')
        )
