from pyface.tasks.api import TaskWindowLayout
from envisage.ui.tasks.api import TasksApplication, TaskWindow
from pyface.api import (ConfirmationDialog, YES, NO, CANCEL)


class WfManager(TasksApplication):
    id = 'force_wfmanager.wfmanager'
    name = 'Workflow Manager'

    def _default_layout_default(self):
        return [TaskWindowLayout(
            'force_wfmanager.wfmanager_task',
            active_task='force_wfmanager.wfmanager_task',
            size=(800, 600)
        )]

    def _window_factory_default(self):
        """Sets a TaskWindow with closing prompt to be the default window
        created by TasksApplication (originally a standard TaskWindow)"""
        return TaskWindowClosePrompt

    # FIXME: This isn't needed if the bug in traitsui/qt4/ui_panel.py is fixed
    def _prepare_exit(self):
        """Same functionality as TasksApplication._prepare_exit(), but
        _save_state is called before application_exiting is fired"""
        self._save_state()
        self.application_exiting = self

    # FIXME: This isn't needed if the bug in traitsui/qt4/ui_panel.py is fixed
    def _application_exiting_fired(self):
        for window in self.windows:
            tasks = window.tasks
            for task in tasks:
                window.remove_task(task)


class TaskWindowClosePrompt(TaskWindow):
    """A TaskWindow which asks if you want to save before closing"""

    def close(self):
        """ Closes the window. It first asks the user to
        save the current Workflow. The user can accept to save, ignore the
        request, or cancel the quit. If the user wants to save, but the save
        fails, the application is not closed so he has a chance to try to
        save again. Overrides close from pyface.tasks.task_window """

        # The attached wfmanager_task for save_methods
        wfmanager_task = self.tasks[0]

        # Pop up for user input
        dialog = ConfirmationDialog(
            parent=None,
            message='Do you want to save before exiting the Workflow '
                    'Manager ?',
            cancel=True,
            yes_label='Save',
            no_label='Don\'t save',
        )
        result = dialog.open()

        # Save
        if result is YES:
            save_result = wfmanager_task.save_workflow()
            # On failed save, don't close the window
            if not save_result:
                return False
            close_result = super(TaskWindowClosePrompt, self).close()
            return close_result

        # Don't save
        elif result is NO:
            close_result = super(TaskWindowClosePrompt, self).close()
            return close_result

        # Cancel
        elif result is CANCEL:
            return False
