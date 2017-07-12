from envisage.api import Plugin
from envisage.ui.tasks.api import TaskFactory
from traits.api import List


class WfManagerPlugin(Plugin):
    """ The basic WfManager """

    # PREFERENCES = 'envisage.preferences'
    # PREFERENCES_PANES = 'envisage.ui.tasks.preferences_panes'
    TASKS = 'envisage.ui.tasks.tasks'

    id = 'force_wfmanager.wfmanager_plugin'
    name = 'Workflow Manager'

    # preferences = List(contributes_to=PREFERENCES)
    # preferences_panes = List(contributes_to=PREFERENCES_PANES)
    tasks = List(contributes_to=TASKS)

    def _tasks_default(self):
        from force_wfmanager.wfmanager_task import WfManagerTask

        return [TaskFactory(id='force_wfmanager.wfmanager_task',
                            name='Workflow Manager',
                            factory=WfManagerTask)]
