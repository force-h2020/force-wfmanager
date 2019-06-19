import os
from unittest import mock, TestCase

from pyface.api import (ConfirmationDialog, YES, NO, CANCEL)
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant

from force_bdss.api import Workflow

from force_wfmanager.model.analysis_model import AnalysisModel
from force_wfmanager.tests import fixtures
from force_wfmanager.wfmanager import TaskWindowClosePrompt

from .mock_methods import mock_file_reader, mock_dialog
from .probe_classes import ProbeWfManager

SETUP_ERROR_PATH = 'force_wfmanager.wfmanager_setup_task.error'
WORKFLOW_READER_PATH = 'force_wfmanager.io.workflow_io.WorkflowReader'
CONFIRMATION_DIALOG_PATH = 'force_wfmanager.wfmanager.ConfirmationDialog'


class TestWfManager(GuiTestAssistant, TestCase):
    def setUp(self):
        super(TestWfManager, self).setUp()
        self.wfmanager = ProbeWfManager()

    def create_tasks(self):

        self.wfmanager.run()
        self.setup_task = self.wfmanager.windows[0].tasks[0]
        self.review_task = self.wfmanager.windows[0].tasks[1]

    def remove_plugins_and_exit(self):
        for plugin in self.wfmanager:
            self.wfmanager.remove_plugin(plugin)
        self.wfmanager.exit()

    def test_init(self):
        self.create_tasks()
        self.assertEqual(len(self.wfmanager.default_layout), 1)
        self.assertEqual(len(self.wfmanager.task_factories), 2)
        self.assertEqual(len(self.wfmanager.windows), 1)
        self.assertEqual(len(self.wfmanager.windows[0].tasks), 2)

        self.assertIsInstance(self.setup_task.analysis_model, AnalysisModel)
        self.assertIsInstance(self.setup_task.workflow_model, Workflow)

        self.assertIsInstance(self.review_task.analysis_model, AnalysisModel)
        self.assertEqual(self.review_task.workflow_model, None)
        self.remove_plugins_and_exit()

    def test_init_with_file(self):
        with mock.patch(WORKFLOW_READER_PATH) as mock_reader:
            mock_reader.side_effect = mock_file_reader
            self.wfmanager = ProbeWfManager(
                fixtures.get('evaluation-4.json'))
            self.create_tasks()
            self.assertEqual(os.path.basename(self.setup_task.current_file),
                             'evaluation-4.json')
            self.assertEqual(mock_reader.call_count, 1)
            self.remove_plugins_and_exit()

    def test_init_with_file_failure(self):
        with mock.patch(SETUP_ERROR_PATH) as mock_error:
            self.wfmanager = ProbeWfManager("this_file_does_not_exist.json")
            self.create_tasks()
            error_msg = ("Cannot read the requested file:\n\n[Errno 2] "
                         "No such file or directory: "
                         "'this_file_does_not_exist.json'")
            mock_error.assert_called_with(
                None,
                error_msg,
                'Error when reading file'
            )

    def test_remove_tasks_on_application_exiting(self):
        self.wfmanager.run()
        self.assertEqual(len(self.wfmanager.windows[0].tasks), 2)
        self.wfmanager.application_exiting = True
        self.assertEqual(len(self.wfmanager.windows[0].tasks), 0)

    def test_switch_task(self):
        self.create_tasks()
        self.assertEqual(
            self.wfmanager.windows[0].active_task,
            self.setup_task,
            msg='Note: this test can fail locally if a saved application '
                'memento exists with the review task in focus'
        )
        self.wfmanager.windows[0].active_task.switch_task()
        self.assertEqual(self.wfmanager.windows[0].active_task,
                         self.review_task)
        self.wfmanager.windows[0].active_task.switch_task()
        self.assertEqual(self.wfmanager.windows[0].active_task,
                         self.setup_task)
        self.remove_plugins_and_exit()

    def test_result_task_exit(self):
        self.create_tasks()
        for window in self.wfmanager.windows:
            window.close = mock.Mock(return_value=True)
        self.review_task.exit()
        self.assertTrue(self.review_task.window.close.called)
        self.remove_plugins_and_exit()

    def test_setup_task_exit(self):
        self.create_tasks()
        for window in self.wfmanager.windows:
            window.close = mock.Mock(return_value=True)
        self.setup_task.exit()
        self.assertTrue(self.setup_task.window.close.called)
        self.remove_plugins_and_exit()


class TestTaskWindowClosePrompt(TestCase):

    def setUp(self):
        super(TestTaskWindowClosePrompt, self).setUp()
        self.wfmanager = ProbeWfManager()
        self.create_tasks()

    def tearDown(self):
        # In case a faulty test hasn't succeeded closing via the dialog
        for plugin in self.wfmanager:
            self.wfmanager.remove_plugin(plugin)
        self.wfmanager.exit()

    def create_tasks(self):
        self.wfmanager.run()
        self.setup_task = self.wfmanager.windows[0].tasks[0]
        self.review_task = self.wfmanager.windows[0].tasks[1]

    def test_exit_application_with_saving(self):
        self.setup_task.save_workflow = mock.Mock(return_value=True)
        window = TaskWindowClosePrompt(application=self.wfmanager)
        with mock.patch(CONFIRMATION_DIALOG_PATH) as mock_confirm_dialog:
            mock_confirm_dialog.side_effect = mock_dialog(
                ConfirmationDialog, YES)
            close_result = window.close()
            self.assertTrue(self.setup_task.save_workflow.called)
            self.assertTrue(close_result)

    def test_exit_application_with_saving_failure(self):
        self.setup_task.save_workflow = mock.Mock(return_value=False)
        window = TaskWindowClosePrompt(application=self.wfmanager)
        with mock.patch(CONFIRMATION_DIALOG_PATH) as mock_confirm_dialog:
            mock_confirm_dialog.side_effect = mock_dialog(
                ConfirmationDialog, YES)
            close_result = window.close()
            self.assertTrue(self.setup_task.save_workflow.called)
            self.assertFalse(close_result)

    def test_exit_application_without_saving(self):
        self.setup_task.save_workflow = mock.Mock(return_value=True)
        window = TaskWindowClosePrompt(application=self.wfmanager)
        with mock.patch(CONFIRMATION_DIALOG_PATH) as mock_confirm_dialog:
            mock_confirm_dialog.side_effect = mock_dialog(
                ConfirmationDialog, NO)
            close_result = window.close()
            self.assertFalse(self.setup_task.save_workflow.called)
            self.assertTrue(close_result)

    def test_cancel_exit_application(self):
        self.setup_task.save_workflow = mock.Mock(return_value=True)
        window = TaskWindowClosePrompt(application=self.wfmanager)
        with mock.patch(CONFIRMATION_DIALOG_PATH) as mock_confirm_dialog:
            mock_confirm_dialog.side_effect = mock_dialog(
                ConfirmationDialog, CANCEL)
            close_result = window.close()
            self.assertFalse(self.setup_task.save_workflow.called)
            self.assertFalse(close_result)
