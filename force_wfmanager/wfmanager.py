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

    def _prepare_exit(self):
        """Same functionality as TasksApplication._prepare_exit(), but
        _save_state is called before application_exiting is fired"""
        self._save_state()
        self.application_exiting = self

    def _application_exiting_fired(self):
        for window in self.windows:
            tasks = window.tasks
            for task in tasks:
                window.remove_task(task)