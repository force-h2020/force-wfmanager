import subprocess
from unittest import mock, TestCase
from testfixtures import LogCapture

from pyface.constant import OK, CANCEL, YES
from pyface.file_dialog import FileDialog
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant

from force_bdss.tests.probe_classes.factory_registry import \
    ProbeFactoryRegistry
from force_bdss.api import MCOProgressEvent, MCOStartEvent
from force_bdss.core.data_value import DataValue

from force_bdss.io.workflow_writer import WorkflowWriter

from force_wfmanager.server.zmq_server import ZMQServer
from force_wfmanager.tests.utils import wait_condition

from .mock_methods import (
    mock_file_reader, mock_file_writer, mock_dialog, mock_return_args,
    mock_file_reader_failure, mock_confirm_function,
    mock_subprocess
)
from .test_wfmanager_tasks import get_probe_wfmanager_tasks

CONFIRMATION_DIALOG_PATH = \
    'force_wfmanager.wfmanager_setup_task.ConfirmationDialog'
FILE_DIALOG_PATH = 'force_wfmanager.wfmanager_setup_task.FileDialog'
INFORMATION_PATH = 'force_wfmanager.wfmanager_setup_task.information'
CONFIRM_PATH = 'force_wfmanager.wfmanager_setup_task.confirm'
FILE_OPEN_PATH = 'force_wfmanager.io.workflow_io.open'
WORKFLOW_WRITER_PATH = 'force_wfmanager.io.workflow_io.WorkflowWriter'
WORKFLOW_READER_PATH = 'force_wfmanager.io.workflow_io.WorkflowReader'
SETUP_ERROR_PATH = 'force_wfmanager.wfmanager_setup_task.error'
SUBPROCESS_PATH = 'force_wfmanager.wfmanager_setup_task.subprocess'
OS_REMOVE_PATH = 'force_wfmanager.wfmanager_setup_task.os.remove'
ZMQSERVER_SETUP_SOCKETS_PATH = \
    'force_wfmanager.wfmanager_setup_task.ZMQServer._setup_sockets'


class TestWFManagerTasks(GuiTestAssistant, TestCase):
    def setUp(self):
        super(TestWFManagerTasks, self).setUp()
        self.setup_task, _ = get_probe_wfmanager_tasks()

    def test_zmq_start(self):
        self.setup_task.zmq_server = mock.Mock(spec=ZMQServer)
        self.setup_task.initialized()
        self.assertTrue(self.setup_task.zmq_server.start.called)

    def test_failed_initialization_of_ui_hooks(self):
        plugin = ProbeFactoryRegistry()

        plugin.ui_hooks_factories[0].create_ui_hooks_manager_raises = True

        self.setup_task.factory_registry = plugin

        with LogCapture() as capture:
            self.assertEqual(len(self.setup_task.ui_hooks_managers), 0)

        capture.check(
            ('force_wfmanager.wfmanager_setup_task',
             'ERROR',
             'Failed to create UI hook manager by factory ProbeUIHooksFactory')
        )

    def test_save_workflow(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer:

            hook_manager = self.setup_task.ui_hooks_managers[0]
            self.assertFalse(hook_manager.before_save_called)

            mock_file_dialog.side_effect = mock_dialog(
                FileDialog, OK, 'file_path')
            mock_writer.side_effect = mock_file_writer

            self.setup_task.save_workflow()

            self.assertTrue(mock_writer.called)
            self.assertTrue(mock_open.called)
            self.assertTrue(mock_file_dialog.called)

            self.assertEqual(self.setup_task.current_file, 'file_path')
            self.assertTrue(hook_manager.before_save_called)

            hook_manager.before_save_raises = True
            with LogCapture() as capture:
                self.setup_task.save_workflow()

            capture.check(('force_wfmanager.wfmanager_setup_task',
                           'ERROR',
                           'Failed before_save hook for hook manager '
                           'ProbeUIHooksManager'))

            hook_manager.before_save_raises = False

        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_writer.side_effect = mock_file_writer

            self.setup_task.save_workflow()

            self.assertTrue(mock_writer.called)
            self.assertTrue(mock_open.called)
            self.assertFalse(mock_file_dialog.called)

    def test_save_workflow_failure(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer:
            mock_file_dialog.side_effect = mock_dialog(
                FileDialog, OK, 'file_path')
            mock_writer.side_effect = mock_file_writer

            self.setup_task.save_workflow()

            self.assertEqual(
                self.setup_task.current_file,
                'file_path'
            )

        mock_open = mock.mock_open()
        mock_open.side_effect = Exception("OUPS")
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(SETUP_ERROR_PATH) as mock_error:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_error.side_effect = mock_return_args

            self.setup_task.save_workflow()

            self.assertEqual(
                self.setup_task.current_file,
                ''
            )

            self.assertTrue(mock_error.called)

    def test_close_saving_dialog(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, CANCEL)
            mock_writer.side_effect = mock_file_writer

            self.setup_task.save_workflow_as()
            mock_open.assert_not_called()

    def test_about_action(self):
        with mock.patch(INFORMATION_PATH) as mock_information:
            mock_information.side_effect = mock_return_args

            self.setup_task.open_about()

            self.assertTrue(mock_information.called)

    def test_save_as_workflow_failure(self):
        mock_open = mock.mock_open()
        mock_open.side_effect = IOError("OUPS")
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(SETUP_ERROR_PATH) as mock_error:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_error.side_effect = mock_return_args

            self.setup_task.save_workflow_as()

            self.assertTrue(mock_open.called)
            mock_error.assert_called_with(
                None,
                'Cannot save in the requested file:\n\nOUPS',
                'Error when saving workflow'
            )

    def test_open_workflow(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_READER_PATH) as mock_reader:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_reader.side_effect = mock_file_reader

            old_workflow = self.setup_task.workflow_model
            self.assertEqual(
                old_workflow,
                self.setup_task.workflow_model)
            self.assertEqual(
                old_workflow,
                self.setup_task.side_pane.workflow_tree.model)

            self.setup_task.open_workflow()

            self.assertTrue(mock_open.called)
            self.assertTrue(mock_reader.called)

            self.assertNotEqual(
                old_workflow,
                self.setup_task.workflow_model)
            self.assertNotEqual(
                old_workflow,
                self.setup_task.side_pane.workflow_tree.model
            )

    def test_read_failure(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(SETUP_ERROR_PATH) as mock_error, \
                mock.patch(WORKFLOW_READER_PATH) as mock_reader:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_error.side_effect = mock_return_args
            mock_reader.side_effect = mock_file_reader_failure

            old_workflow = self.setup_task.workflow_model

            self.setup_task.open_workflow()

            self.assertTrue(mock_open.called)
            self.assertTrue(mock_reader.called)
            mock_error.assert_called_with(
                None,
                'Cannot read the requested file:\n\nOUPS',
                'Error when reading file'
            )
            self.assertEqual(old_workflow, self.setup_task.workflow_model)

    def test_dispatch_mco_event(self):
        send_event = self.setup_task._server_event_callback
        self.assertEqual(self.setup_task.analysis_model.value_names, ())
        with self.event_loop():
            send_event(MCOStartEvent(
                parameter_names=["x"],
                kpi_names=["y"])
            )

        self.assertEqual(
            len(self.setup_task.analysis_model.evaluation_steps),
            0)
        self.assertEqual(
            self.setup_task.analysis_model.value_names,
            ('x', 'y', 'y weight'))

        with self.event_loop():
            send_event(MCOProgressEvent(
                optimal_point=[
                    DataValue(value=1.0)
                ],
                optimal_kpis=[
                    DataValue(value=2.0)
                ],
                weights=[1.0]))

        self.assertEqual(
            len(self.setup_task.analysis_model.evaluation_steps),
            1)

    def test_initialize_finalize(self):
        self.setup_task.zmq_server.start()
        wait_condition(
            lambda: (self.setup_task.zmq_server.state ==
                     ZMQServer.STATE_WAITING))

        self.setup_task.zmq_server.stop()

        self.assertEqual(
            self.setup_task.zmq_server.state,
            ZMQServer.STATE_STOPPED)

    def test_zmq_server_failure(self):
        with mock.patch(ZMQSERVER_SETUP_SOCKETS_PATH) as setup_sockets, \
                mock.patch(SETUP_ERROR_PATH) as mock_error, \
                self.event_loop_until_condition(lambda: mock_error.called):

            setup_sockets.side_effect = Exception("boom")
            self.setup_task.zmq_server.start()

    def test_open_plugin_dialog(self):

        with self.event_loop():
            self.setup_task.open_plugins()

    def test_run_bdss(self):

        self.setup_task.analysis_model.value_names = ('x', )
        self.setup_task.analysis_model.add_evaluation_step((2.0, ))
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

            hook_manager = self.setup_task.ui_hooks_managers[0]

            self.assertTrue(self.setup_task.side_pane.ui_enabled)
            self.assertFalse(hook_manager.before_execution_called)
            self.assertFalse(hook_manager.after_execution_called)

            with self.event_loop_until_condition(
                    lambda: _mock_subprocess.check_call.called):
                self.setup_task.run_bdss()

            with self.event_loop_until_condition(
                    lambda: self.setup_task.side_pane.ui_enabled):
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

            hook_manager = self.setup_task.ui_hooks_managers[0]
            hook_manager.before_execution_raises = True
            with LogCapture() as capture, \
                    self.event_loop_until_condition(
                        lambda: _mock_subprocess.check_call.called):
                self.setup_task.run_bdss()

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
                self.setup_task.run_bdss()

            capture.check(
                ('force_wfmanager.wfmanager_setup_task',
                 'ERROR',
                 'Failed after_execution hook for hook manager '
                 'ProbeUIHooksManager')
            )

    def test_run_bdss_cancel(self):
        self.setup_task.analysis_model.value_names = ('x', )
        self.setup_task.analysis_model.add_evaluation_step((2.0, ))
        with mock.patch(CONFIRM_PATH) as mock_confirm:
            mock_confirm.side_effect = mock_confirm_function(CANCEL)

            self.assertTrue(self.setup_task.side_pane.ui_enabled)
            self.setup_task.run_bdss()
            self.assertTrue(self.setup_task.side_pane.ui_enabled)

            mock_confirm.assert_called_with(
                None,
                "Are you sure you want to run the computation and "
                "empty the result table?"
            )

    def test_run_bdss_failure(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer, \
                mock.patch(SUBPROCESS_PATH + ".check_call") as mock_chk_call, \
                mock.patch(SETUP_ERROR_PATH) as mock_error:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_writer.side_effect = mock_file_writer
            mock_error.side_effect = mock_return_args

            def _check_exception_behavior(exception):
                mock_chk_call.side_effect = exception

                self.assertTrue(self.setup_task.side_pane.ui_enabled)

                with self.event_loop_until_condition(
                        lambda: mock_chk_call.called):
                    self.setup_task.run_bdss()

                ui_enabled = self.setup_task.side_pane.ui_enabled
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
                        "Execution of BDSS failed. \n\n" + msg))

    def test_run_bdss_write_failure(self):
        with mock.patch(WORKFLOW_WRITER_PATH) as mock_writer, \
                mock.patch(SETUP_ERROR_PATH) as mock_error:
            workflow_writer = mock.Mock(spec=WorkflowWriter)
            workflow_writer.write.side_effect = Exception("write failed")
            mock_writer.return_value = workflow_writer
            mock_error.side_effect = mock_return_args

            self.assertTrue(self.setup_task.side_pane.ui_enabled)

            self.setup_task.run_bdss()

            self.assertTrue(self.setup_task.side_pane.ui_enabled)

            self.assertEqual(
                mock_error.call_args[0][1],
                'Unable to run BDSS: write failed')
