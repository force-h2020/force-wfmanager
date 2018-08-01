import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from force_wfmanager.wfmanager import WfManager, TaskWindowClosePrompt
from force_wfmanager.wfmanager_task import WfManagerTask
from pyface.api import (ConfirmationDialog, YES, NO, CANCEL)

CONFIRMATION_DIALOG_PATH = 'force_wfmanager.wfmanager.ConfirmationDialog'


def mock_dialog(dialog_class, result, path=''):
    def mock_dialog_call(*args, **kwargs):
        dialog = mock.Mock(spec=dialog_class)
        dialog.open = lambda: result
        dialog.path = path
        return dialog
    return mock_dialog_call


class TestWfManager(unittest.TestCase):

    def test_wfmanager(self):
        wfmanager = WfManager()
        self.assertEqual(len(wfmanager.default_layout), 1)


class TestTaskWindowClosePrompt(unittest.TestCase):

    def test_exit_application_with_saving(self):
        wfmanager_task = WfManagerTask()
        wfmanager_task.save_workflow = mock.Mock(return_value=True)
        window = TaskWindowClosePrompt(tasks=[wfmanager_task])
        with mock.patch(CONFIRMATION_DIALOG_PATH) as mock_confirm_dialog:
            mock_confirm_dialog.side_effect = mock_dialog(
                ConfirmationDialog, YES)
            close_result = window.close()
            self.assertTrue(wfmanager_task.save_workflow.called)
            self.assertTrue(close_result)

    def test_exit_application_with_saving_failure(self):
        wfmanager_task = WfManagerTask()
        wfmanager_task.save_workflow = mock.Mock(return_value=False)
        window = TaskWindowClosePrompt(tasks=[wfmanager_task])
        with mock.patch(CONFIRMATION_DIALOG_PATH) as mock_confirm_dialog:
            mock_confirm_dialog.side_effect = mock_dialog(
                ConfirmationDialog, YES)
            close_result = window.close()
            self.assertTrue(wfmanager_task.save_workflow.called)
            self.assertFalse(close_result)

    def test_exit_application_without_saving(self):
        wfmanager_task = WfManagerTask()
        wfmanager_task.save_workflow = mock.Mock(return_value=True)
        window = TaskWindowClosePrompt(tasks=[wfmanager_task])
        with mock.patch(CONFIRMATION_DIALOG_PATH) as mock_confirm_dialog:
            mock_confirm_dialog.side_effect = mock_dialog(
                ConfirmationDialog, NO)
            close_result = window.close()
            self.assertFalse(wfmanager_task.save_workflow.called)
            self.assertTrue(close_result)

    def test_cancel_exit_application(self):
        wfmanager_task = WfManagerTask()
        wfmanager_task.save_workflow = mock.Mock(return_value=True)
        window = TaskWindowClosePrompt(tasks=[wfmanager_task])
        with mock.patch(CONFIRMATION_DIALOG_PATH) as mock_confirm_dialog:
            mock_confirm_dialog.side_effect = mock_dialog(
                ConfirmationDialog, CANCEL)
            close_result = window.close()
            self.assertFalse(wfmanager_task.save_workflow.called)
            self.assertFalse(close_result)
