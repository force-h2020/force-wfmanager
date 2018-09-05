import logging

from envisage.ui.tasks.api import TasksApplication, TaskWindow

from pyface.api import (CANCEL, ConfirmationDialog, NO, YES)
from pyface.tasks.api import TaskWindowLayout

log = logging.getLogger(__name__)


class WfManager(TasksApplication):
    id = 'force_wfmanager.wfmanager'
    name = 'Workflow Manager'

    # Overridden defaults from TasksApplication/Application

    def _default_layout_default(self):
        tasks = [factory.id for factory in self.task_factories]
        return [TaskWindowLayout(
            *tasks,
            active_task='force_wfmanager.wfmanager_setup_task',
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
        self._remove_tasks()

    def _remove_tasks(self):
        """Removes the task elements from all windows in the application.
        Part of a workaround for a bug in traitsui/qt4/ui_panel.py where
        sizeHint() would be called, even when a Widget was already destroyed"""
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

        # The attached wfmanager_setup_task for saving methods
        setup_task = None
        for window in self.application.windows:
            for task in window.tasks:
                if task.name == "Workflow Setup":
                    setup_task = task
        # If we don't have a setup task for some reason, just close
        if setup_task is None:
            return True

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
            save_result = setup_task.save_workflow()

            # On a failed save, don't close the window
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
