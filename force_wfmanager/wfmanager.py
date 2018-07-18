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

    def delete_tasks(self):
        for window in self.windows:
            tasks = window.tasks
            for task in tasks:
                window.remove_task(task)

    def _application_exiting_fired(self):
        """An event fired immediately before the GUI event loop is ended.
        Is fired for both the menu-bar exit / Cmd-Q and clicking the title
        bar exit button"""
        self.delete_tasks()
