import unittest

from testfixtures import LogCapture

from unittest import mock
import subprocess

from pyface.api import (YES, CANCEL, FileDialog, OK)

from pyface.tasks.api import TaskLayout, TaskWindow

from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant

from force_bdss.tests.probe_classes.factory_registry_plugin import \
    ProbeFactoryRegistryPlugin
from force_bdss.api import WorkflowWriter

from force_wfmanager.wfmanager import WfManager
from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask
from force_wfmanager.wfmanager_results_task import WfManagerResultsTask
from force_wfmanager.left_side_pane.tree_pane import TreePane
from force_wfmanager.left_side_pane.workflow_tree import WorkflowTree

from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin

from force_wfmanager.wfmanager_plugin import WfManagerPlugin

FILE_DIALOG_PATH = 'force_wfmanager.wfmanager.FileDialog'
INFORMATION_PATH = 'force_wfmanager.wfmanager.information'
CONFIRM_PATH = 'force_wfmanager.wfmanager_setup_task.confirm'
FILE_OPEN_PATH = 'force_wfmanager.wfmanager.open'
WORKFLOW_WRITER_PATH = 'force_wfmanager.wfmanager_setup_task.WorkflowWriter'
WORKFLOW_READER_PATH = 'force_wfmanager.wfmanager.WorkflowReader'
ERROR_PATH = 'force_wfmanager.wfmanager_setup_task.error'
SUBPROCESS_PATH = 'force_wfmanager.wfmanager_setup_task.subprocess'
OS_REMOVE_PATH = 'force_wfmanager.wfmanager_setup_task.os.remove'
ZMQSERVER_SETUP_SOCKETS_PATH = \
    'force_wfmanager.wfmanager.ZMQServer._setup_sockets'


def get_wfmanager_task(task_name):
    if task_name == "Setup":
        wfmanager_task = WfManagerSetupTask()
    elif task_name == "Results":
        wfmanager_task = WfManagerResultsTask()
    else:
        raise ValueError
    wfmanager_task.window = mock.Mock(spec=TaskWindow)
    wfmanager_task.window.application = dummy_wfmanager()

    wfmanager_task.window.application.factory_registry = \
        ProbeFactoryRegistryPlugin()
    wfmanager_task.window.application.exit = mock.Mock()

    wfmanager_task.create_central_pane()
    wfmanager_task.create_dock_panes()

    return wfmanager_task


def mock_file_writer(*args, **kwargs):
    def write(*args, **kwargs):
        return ''
    writer = mock.Mock(spec=WorkflowWriter)
    writer.write = write
    return writer


def mock_confirm_function(result):
    def mock_conf(*args, **kwargs):
        return result
    return mock_conf


def mock_dialog(dialog_class, result, path=''):
    def mock_dialog_call(*args, **kwargs):
        dialog = mock.Mock(spec=dialog_class)
        dialog.open = lambda: result
        dialog.path = path
        return dialog
    return mock_dialog_call


def mock_subprocess(*args, **kwargs):
    def check_call(*args, **kwargs):
        return
    mock_subprocess_module = mock.Mock(spec=subprocess)
    mock_subprocess_module.check_call = check_call
    return mock_subprocess_module


def mock_show_error(*args, **kwargs):
    return args


def dummy_wfmanager():

    plugins = [CorePlugin(), TasksPlugin(), WfManagerPlugin()]
    wfmanager = WfManager(plugins=plugins, workflow_file=None)
    wfmanager.run = lambda: None
    return wfmanager


class TestWFManagerTasks(GuiTestAssistant, unittest.TestCase):
    def setUp(self):
        super(TestWFManagerTasks, self).setUp()
        self.wfmanager_setup_task = get_wfmanager_task("Setup")
        self.wfmanager_results_task = get_wfmanager_task("Results")

    def test_init(self):
        self.assertEqual(len(self.wfmanager_setup_task.create_dock_panes()), 1)
        self.assertIsInstance(self.wfmanager_setup_task.side_pane, TreePane)
        self.assertIsInstance(
            self.wfmanager_setup_task.side_pane.workflow_tree, WorkflowTree)
        self.assertIsInstance(self.wfmanager_setup_task.default_layout,
                              TaskLayout)

    def test_run_bdss(self):
        self.wfmanager_setup_task.app.analysis_m.value_names = ('x', )
        self.wfmanager_setup_task.app.analysis_m.add_evaluation_step((2.0, ))
        mock_open = mock.mock_open()
        with mock.patch(CONFIRM_PATH) as mock_confirm, \
                mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer, \
                mock.patch(SUBPROCESS_PATH) as _mock_subprocess:
            mock_confirm.side_effect = mock_confirm_function(YES)
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_writer.side_effect = mock_file_writer
            mock_subprocess.side_effect = mock_subprocess

            hook_manager = self.wfmanager_setup_task.app.ui_hooks_managers[0]

            self.assertTrue(self.wfmanager_setup_task.side_pane.ui_enabled)
            self.assertFalse(hook_manager.before_execution_called)
            self.assertFalse(hook_manager.after_execution_called)

            with self.event_loop_until_condition(
                    lambda: _mock_subprocess.check_call.called):
                self.wfmanager_setup_task.run_bdss()

            with self.event_loop_until_condition(
                    lambda: self.wfmanager_setup_task.side_pane.ui_enabled):
                pass

            self.assertTrue(hook_manager.before_execution_called)
            self.assertTrue(hook_manager.after_execution_called)

    def test_hook_manager_raises(self):
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer, \
                mock.patch(SUBPROCESS_PATH) as _mock_subprocess:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_writer.side_effect = mock_file_writer
            mock_subprocess.side_effect = mock_subprocess

            hook_manager = self.wfmanager_setup_task.app.ui_hooks_managers[0]
            hook_manager.before_execution_raises = True
            with LogCapture() as capture, \
                    self.event_loop_until_condition(
                        lambda: _mock_subprocess.check_call.called):
                self.wfmanager_setup_task.run_bdss()

            capture.check(
                ('force_wfmanager.wfmanager_setup_task',
                 'ERROR',
                 'Failed before_execution hook for hook manager '
                 'ProbeUIHooksManager')
            )
            hook_manager.before_execution_raises = False
            hook_manager.after_execution_raises = True
            with LogCapture() as capture, \
                    self.event_loop_until_condition(
                        lambda: _mock_subprocess.check_call.called):
                self.wfmanager_setup_task.run_bdss()

            capture.check(
                ('force_wfmanager.wfmanager_setup_task',
                 'ERROR',
                 'Failed after_execution hook for hook manager '
                 'ProbeUIHooksManager')
            )

    def test_run_bdss_cancel(self):
        self.wfmanager_setup_task.app.analysis_m.value_names = ('x', )
        self.wfmanager_setup_task.app.analysis_m.add_evaluation_step((2.0, ))
        with mock.patch(CONFIRM_PATH) as mock_confirm:
            mock_confirm.side_effect = mock_confirm_function(CANCEL)

            self.assertTrue(self.wfmanager_setup_task.side_pane.ui_enabled)
            self.wfmanager_setup_task.run_bdss()
            self.assertTrue(self.wfmanager_setup_task.side_pane.ui_enabled)

            mock_confirm.assert_called_with(
                None,
                "Are you sure you want to run the computation and "
                "empty the result table?"
            )

    def test_run_bdss_failure(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer, \
                mock.patch(SUBPROCESS_PATH+".check_call") as mock_check_call, \
                mock.patch(ERROR_PATH) as mock_error:
            mock_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_writer.side_effect = mock_file_writer
            mock_error.side_effect = mock_show_error

            def _check_exception_behavior(exception):
                mock_check_call.side_effect = exception

                self.assertTrue(self.wfmanager_setup_task.side_pane.ui_enabled)

                with self.event_loop_until_condition(
                        lambda: mock_check_call.called):
                    self.wfmanager_setup_task.run_bdss()

                ui_enabled = self.wfmanager_setup_task.side_pane.ui_enabled
                with self.event_loop_until_condition(lambda: ui_enabled):
                    pass

                return mock_error.call_args[0][1]

            for exc, msg in [
                    (Exception("boom"), 'boom'),
                    (subprocess.CalledProcessError(1, "fake_command"),
                        "Command 'fake_command' returned non-zero exit "
                        "status 1"),
                    (OSError("whatever"), "whatever")]:
                self.assertTrue(
                    _check_exception_behavior(exc).startswith(
                        "Execution of BDSS failed. \n\n"+msg))

    def test_run_bdss_write_failure(self):
        with mock.patch(WORKFLOW_WRITER_PATH) as mock_writer, \
                mock.patch(ERROR_PATH) as mock_error:
            workflow_writer = mock.Mock(spec=WorkflowWriter)
            workflow_writer.write.side_effect = Exception("write failed")
            mock_writer.return_value = workflow_writer
            mock_error.side_effect = mock_show_error

            self.assertTrue(self.wfmanager_setup_task.side_pane.ui_enabled)

            self.wfmanager_setup_task.run_bdss()

            self.assertTrue(self.wfmanager_setup_task.side_pane.ui_enabled)

            self.assertEqual(
                mock_error.call_args[0][1],
                'Unable to run BDSS: write failed')
