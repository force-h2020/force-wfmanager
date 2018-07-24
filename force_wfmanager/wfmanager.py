from pyface.tasks.api import TaskWindowLayout
from envisage.ui.tasks.api import TasksApplication


class WfManager(TasksApplication):
    id = 'force_wfmanager.wfmanager'
    name = 'Workflow Manager'

    def _default_layout_default(self):
        return [TaskWindowLayout(
            'force_wfmanager.wfmanager_task',
            active_task='force_wfmanager.wfmanager_task',
            size=(800, 600)
        )]
