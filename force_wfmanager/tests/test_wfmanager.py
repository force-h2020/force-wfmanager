from unittest import mock, TestCase

from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin

from pyface.api import (ConfirmationDialog, YES, NO, CANCEL)
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant

from force_bdss.api import (Workflow, WorkflowReader)
from force_bdss.tests.probe_classes.factory_registry import (
    ProbeFactoryRegistry
)

from force_wfmanager.ui.wfmanager_plugin import WfManagerPlugin
from force_wfmanager.model.analysis_model import AnalysisModel
from force_wfmanager.tests import fixtures
from force_wfmanager.wfmanager import WfManager, TaskWindowClosePrompt
from force_wfmanager.wfmanager_results_task import WfManagerResultsTask
from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask

WORKFLOW_READER_PATH = 'force_wfmanager.wfmanager_setup_task.WorkflowReader'
CONFIRMATION_DIALOG_PATH = 'force_wfmanager.wfmanager.ConfirmationDialog'


def dummy_wfmanager(filename=None):
    plugins = [CorePlugin(), TasksPlugin(),
               mock_wfmanager_plugin(filename)]
    wfmanager = WfManager(plugins=plugins)
    # 'Run' the application by creating windows without an event loop
    wfmanager.run = wfmanager._create_windows
    return wfmanager


def mock_wfmanager_plugin(filename):
    plugin = WfManagerPlugin()
    plugin._create_setup_task = mock_create_setup_task(filename)
    plugin._create_results_task = mock_create_results_task()
    return plugin


def mock_create_setup_task(filename):
    def func():
        wf_manager_task = WfManagerSetupTask(
            factory_registry=ProbeFactoryRegistry())
        if filename is not None:
            wf_manager_task.open_workflow_file(filename)
        return wf_manager_task
    return func


def mock_create_results_task():
    def func():
        wf_manager_task = WfManagerResultsTask(
            factory_registry=ProbeFactoryRegistry())
        return wf_manager_task
    return func


def mock_dialog(dialog_class, result, path=''):
    def mock_dialog_call(*args, **kwargs):
        dialog = mock.Mock(spec=dialog_class)
        dialog.open = lambda: result
        dialog.path = path
        return dialog
    return mock_dialog_call


def mock_file_reader(*args, **kwargs):
    def read(*args, **kwargs):
        workflow = Workflow()
        return workflow
    reader = mock.Mock(spec=WorkflowReader)
    reader.read = read
    return reader


def mock_window(wfmanager):
    window = mock.Mock(TaskWindowClosePrompt)
    window.application = wfmanager
    return window


class TestWfManager(GuiTestAssistant, TestCase):
    def setUp(self):
        super(TestWfManager, self).setUp()
        self.wfmanager = dummy_wfmanager()

    def create_tasks(self):

        self.wfmanager.run()
        self.setup_task = self.wfmanager.windows[0].tasks[0]
        self.results_task = self.wfmanager.windows[0].tasks[1]

    def test_init(self):
        self.create_tasks()
        self.assertEqual(len(self.wfmanager.default_layout), 1)
        self.assertEqual(len(self.wfmanager.task_factories), 2)
        self.assertEqual(len(self.wfmanager.windows), 1)
        self.assertEqual(len(self.wfmanager.windows[0].tasks), 2)

        self.assertIsInstance(self.setup_task.analysis_model, AnalysisModel)
        self.assertIsInstance(self.setup_task.workflow_model, Workflow)

        self.assertIsInstance(self.results_task.analysis_model, AnalysisModel)
        self.assertEqual(self.results_task.workflow_model, None)

    def test_init_with_file(self):
        with mock.patch(WORKFLOW_READER_PATH) as mock_reader:
            mock_reader.side_effect = mock_file_reader
            self.wfmanager = dummy_wfmanager(fixtures.get('evaluation-4.json'))
            self.create_tasks()
            self.assertEqual(self.setup_task.current_file.split('/')[-1],
                             'evaluation-4.json')
            self.assertEqual(mock_reader.call_count, 1)

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
                'memento exists with the results task in focus'
        )
        self.wfmanager.windows[0].active_task.switch_task()
        self.assertEqual(self.wfmanager.windows[0].active_task,
                         self.results_task)
        self.wfmanager.windows[0].active_task.switch_task()
        self.assertEqual(self.wfmanager.windows[0].active_task,
                         self.setup_task)

    def test_result_task_exit(self):
        self.create_tasks()
        for window in self.wfmanager.windows:
            window.close = mock.Mock(return_value=True)
        self.results_task.exit()
        self.assertTrue(self.results_task.window.close.called)

    def test_setup_task_exit(self):
        self.create_tasks()
        for window in self.wfmanager.windows:
            window.close = mock.Mock(return_value=True)
        self.setup_task.exit()
        self.assertTrue(self.setup_task.window.close.called)


class TestTaskWindowClosePrompt(TestCase):

    def setUp(self):
        super(TestTaskWindowClosePrompt, self).setUp()
        self.wfmanager = dummy_wfmanager()
        self.create_tasks()

    def create_tasks(self):
        self.wfmanager.run()
        self.setup_task = self.wfmanager.windows[0].tasks[0]
        self.results_task = self.wfmanager.windows[0].tasks[1]

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
