#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

from unittest import mock, TestCase
import subprocess
from testfixtures import LogCapture

from pyface.constant import OK, CANCEL, YES
from pyface.file_dialog import FileDialog
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant

from force_bdss.api import (
    DataValue,
    MCOProgressEvent,
    MCOStartEvent,
    WorkflowWriter,
    plugin_id,
)
from force_bdss.tests.probe_classes.factory_registry import (
    ProbeFactoryRegistry,
)

from force_wfmanager.server.zmq_server import ZMQServer
from force_wfmanager.tests.dummy_classes.dummy_contributed_ui import (
    DummyContributedUI2,
)
from force_wfmanager.tests.dummy_classes.dummy_wfmanager import (
    DummyUIWfManager
)
from force_wfmanager.tests.dummy_classes.dummy_events import (
    ProbeUIRuntimeEvent)
from force_wfmanager.tests.utils import wait_condition

from .mock_methods import (
    mock_file_reader,
    mock_file_writer,
    mock_dialog,
    mock_return_args,
    mock_file_reader_failure,
    mock_confirm_function,
    mock_subprocess,
)
from .test_wfmanager_tasks import get_probe_wfmanager_tasks

CONFIRMATION_DIALOG_PATH = (
    "force_wfmanager.wfmanager_setup_task.ConfirmationDialog"
)
FILE_DIALOG_PATH = "force_wfmanager.wfmanager_setup_task.FileDialog"
INFORMATION_PATH = "force_wfmanager.wfmanager_setup_task.information"
CONFIRM_PATH = "force_wfmanager.wfmanager_setup_task.confirm"
FILE_OPEN_PATH = "force_wfmanager.io.workflow_io.WorkflowWriter.write"
WORKFLOW_WRITER_PATH = "force_wfmanager.io.workflow_io.WorkflowWriter"
WORKFLOW_READER_PATH = "force_wfmanager.io.workflow_io.WorkflowReader"
SETUP_ERROR_PATH = "force_wfmanager.wfmanager_setup_task.error"
SUBPROCESS_PATH = "force_wfmanager.wfmanager_setup_task.subprocess"
OS_REMOVE_PATH = "force_wfmanager.wfmanager_setup_task.os.remove"
ZMQSERVER_SETUP_SOCKETS_PATH = (
    "force_wfmanager.wfmanager_setup_task.ZMQServer._setup_sockets"
)
UI_SELECT_MODAL_PATH = "force_wfmanager.wfmanager_setup_task.UISelectModal"
RUN_BDSS_PATH = (
    "force_wfmanager.wfmanager_setup_task.WfManagerSetupTask.run_bdss"
)


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
            (
                "force_wfmanager.wfmanager_setup_task",
                "ERROR",
                "Failed to create UI hook manager by "
                "factory ProbeUIHooksFactory",
            )
        )

    def test_save_workflow(self):

        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, mock.patch(
            WORKFLOW_WRITER_PATH
        ) as mock_writer:

            hook_manager = self.setup_task.ui_hooks_managers[0]
            self.assertFalse(hook_manager.before_save_called)

            mock_file_dialog.side_effect = mock_dialog(
                FileDialog, OK, "file_path"
            )
            mock_writer.side_effect = mock_file_writer

            self.setup_task.save_workflow()

            self.assertTrue(mock_writer.called)
            self.assertTrue(mock_file_dialog.called)

            self.assertEqual(self.setup_task.current_file, "file_path")
            self.assertTrue(hook_manager.before_save_called)

            hook_manager.before_save_raises = True
            with LogCapture() as capture:
                self.setup_task.save_workflow()

            capture.check(
                (
                    "force_wfmanager.wfmanager_setup_task",
                    "ERROR",
                    "Failed before_save hook for hook manager "
                    "ProbeUIHooksManager",
                )
            )

            hook_manager.before_save_raises = False

        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, mock.patch(
            WORKFLOW_WRITER_PATH
        ) as mock_writer:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_writer.side_effect = mock_file_writer

            self.setup_task.save_workflow()

            self.assertTrue(mock_writer.called)
            self.assertFalse(mock_file_dialog.called)

    def test_save_workflow_success(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, mock.patch(
            FILE_OPEN_PATH, mock_open, create=True
        ):
            mock_file_dialog.side_effect = mock_dialog(
                FileDialog, OK, "file_path"
            )

            self.assertTrue(self.setup_task.save_workflow())

            self.assertEqual(self.setup_task.current_file, "file_path")

    def test_save_workflow_failure(self):
        mock_open = mock.mock_open()
        mock_open.side_effect = Exception("OUPS")
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, mock.patch(
            FILE_OPEN_PATH, mock_open, create=True
        ), mock.patch(SETUP_ERROR_PATH) as mock_error:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_error.side_effect = mock_return_args

            self.assertFalse(self.setup_task.save_workflow())

            self.assertEqual(self.setup_task.current_file, "")

            self.assertTrue(mock_error.called)

    def test_close_saving_dialog(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, mock.patch(
            FILE_OPEN_PATH, mock_open, create=True
        ), mock.patch(WORKFLOW_WRITER_PATH) as mock_writer:
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
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, mock.patch(
            FILE_OPEN_PATH, mock_open, create=True
        ), mock.patch(SETUP_ERROR_PATH) as mock_error:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_error.side_effect = mock_return_args

            self.setup_task.save_workflow_as()

            mock_error.assert_called_with(
                None,
                "Cannot save in the requested file:\n\nOUPS",
                "Error when saving workflow",
            )

    def test_open_workflow(self):
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, mock.patch(
            WORKFLOW_READER_PATH
        ) as mock_reader:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_reader.side_effect = mock_file_reader

            old_workflow = self.setup_task.workflow_model
            self.assertEqual(old_workflow, self.setup_task.workflow_model)
            self.assertEqual(
                old_workflow, self.setup_task.side_pane.workflow_tree.model
            )

            with mock.patch(
                "force_wfmanager.wfmanager_setup_task.load_analysis_model"
            ) as mock_read:
                mock_read.return_value = {}
                self.setup_task.open_workflow()

            self.assertTrue(mock_reader.called)

            self.assertNotEqual(old_workflow, self.setup_task.workflow_model)
            self.assertNotEqual(
                old_workflow, self.setup_task.side_pane.workflow_tree.model
            )

            with mock.patch(INFORMATION_PATH) as mock_information:
                with mock.patch(
                    "force_wfmanager.wfmanager_setup_task.load_analysis_model"
                ) as mock_read:
                    mock_read.return_value = {"some": "data"}
                    self.setup_task.open_workflow()
                    mock_information.assert_called()

    def test_read_failure(self):
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, mock.patch(
            SETUP_ERROR_PATH
        ) as mock_error, mock.patch(WORKFLOW_READER_PATH) as mock_reader:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_error.side_effect = mock_return_args
            mock_reader.side_effect = mock_file_reader_failure

            old_workflow = self.setup_task.workflow_model

            self.setup_task.open_workflow()

            self.assertTrue(mock_reader.called)
            mock_error.assert_called_with(
                None,
                "Cannot read the requested file:\n\nOUPS",
                "Error when reading file",
            )
            self.assertEqual(old_workflow, self.setup_task.workflow_model)

    def test_dispatch_mco_event(self):
        send_event = self.setup_task._server_event_callback
        self.assertEqual(self.setup_task.analysis_model.header, ())
        with self.event_loop():
            send_event(MCOStartEvent(parameter_names=["x"], kpi_names=["y"]))

        self.assertEqual(
            0, len(self.setup_task.analysis_model.evaluation_steps)
        )
        self.assertEqual(
            0, len(self.setup_task.analysis_model.step_metadata)
        )
        self.assertEqual(
            ("x", "y"), self.setup_task.analysis_model.header
        )

        with self.event_loop():
            send_event(
                ProbeUIRuntimeEvent()
            )

        with self.event_loop():
            send_event(
                MCOProgressEvent(
                    optimal_point=[DataValue(value=1.0)],
                    optimal_kpis=[DataValue(value=2.0)],
                )
            )

        self.assertEqual(
            1, len(self.setup_task.analysis_model.evaluation_steps)
        )
        self.assertEqual(
            1, len(self.setup_task.analysis_model.step_metadata)
        )

    def test_initialize_finalize(self):
        self.setup_task.zmq_server.start()
        wait_condition(
            lambda: (
                self.setup_task.zmq_server.state == ZMQServer.STATE_WAITING
            )
        )

        self.setup_task.zmq_server.stop()

        self.assertEqual(
            self.setup_task.zmq_server.state, ZMQServer.STATE_STOPPED
        )

    def test_zmq_server_failure(self):
        with mock.patch(
            ZMQSERVER_SETUP_SOCKETS_PATH
        ) as setup_sockets, mock.patch(
            SETUP_ERROR_PATH
        ) as mock_error, self.event_loop_until_condition(
            lambda: mock_error.called
        ):

            setup_sockets.side_effect = Exception("boom")
            self.setup_task.zmq_server.start()

    def test_open_plugin_dialog(self):

        with self.event_loop():
            self.setup_task.open_plugins()

    def test_run_bdss(self):

        self.setup_task.analysis_model.header = ("x",)
        self.setup_task.analysis_model.notify((2.0,))
        mock_open = mock.mock_open()
        with mock.patch(CONFIRM_PATH) as mock_confirm, mock.patch(
            FILE_DIALOG_PATH
        ) as mock_file_dialog, mock.patch(
            FILE_OPEN_PATH, mock_open, create=True
        ), mock.patch(
            WORKFLOW_WRITER_PATH
        ) as mock_writer, mock.patch(
            SUBPROCESS_PATH
        ) as _mock_subprocess:
            mock_confirm.side_effect = mock_confirm_function(YES)
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_writer.side_effect = mock_file_writer
            mock_subprocess.side_effect = mock_subprocess

            hook_manager = self.setup_task.ui_hooks_managers[0]

            self.assertTrue(self.setup_task.side_pane.ui_enabled)
            self.assertTrue(self.setup_task.setup_pane.ui_enabled)
            self.assertFalse(hook_manager.before_execution_called)
            self.assertFalse(hook_manager.after_execution_called)

            with self.event_loop_until_condition(
                lambda: _mock_subprocess.check_call.called
            ):
                self.setup_task.run_bdss()

            with self.event_loop_until_condition(
                lambda: self.setup_task.side_pane.ui_enabled
            ):
                pass

            with self.event_loop_until_condition(
                lambda: self.setup_task.setup_pane.ui_enabled
            ):
                pass

            self.assertTrue(hook_manager.before_execution_called)
            self.assertTrue(hook_manager.after_execution_called)

    def test_hook_manager_raises(self):
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, mock.patch(
            WORKFLOW_WRITER_PATH
        ) as mock_writer, mock.patch(SUBPROCESS_PATH) as _mock_subprocess:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_writer.side_effect = mock_file_writer
            mock_subprocess.side_effect = mock_subprocess

            hook_manager = self.setup_task.ui_hooks_managers[0]
            hook_manager.before_execution_raises = True
            with LogCapture() as capture, self.event_loop_until_condition(
                lambda: _mock_subprocess.check_call.called
            ):
                self.setup_task.run_bdss()

            self.assertIn(
                (
                    "force_wfmanager.wfmanager_setup_task",
                    "ERROR",
                    "Failed before_execution hook for hook manager "
                    "ProbeUIHooksManager",
                ),
                capture.actual(),
            )

            hook_manager.before_execution_raises = False
            hook_manager.after_execution_raises = True
            with LogCapture() as capture, self.event_loop_until_condition(
                lambda: _mock_subprocess.check_call.called
            ):
                self.setup_task.run_bdss()

            self.assertIn(
                (
                    "force_wfmanager.wfmanager_setup_task",
                    "ERROR",
                    "Failed after_execution hook for hook manager "
                    "ProbeUIHooksManager",
                ),
                capture.actual(),
            )

    def test_run_bdss_cancel(self):
        self.setup_task.analysis_model.header = ("x",)
        self.setup_task.analysis_model.notify((2.0,))
        with mock.patch(CONFIRM_PATH) as mock_confirm:
            mock_confirm.side_effect = mock_confirm_function(CANCEL)

            self.assertTrue(self.setup_task.side_pane.ui_enabled)
            self.setup_task.run_bdss()
            self.assertTrue(self.setup_task.side_pane.ui_enabled)

            mock_confirm.assert_called_with(
                None,
                "Are you sure you want to run the computation and "
                "empty the result table?",
            )

    def test_run_bdss_failure(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, mock.patch(
            FILE_OPEN_PATH, mock_open, create=True
        ), mock.patch(WORKFLOW_WRITER_PATH) as mock_writer, mock.patch(
            SUBPROCESS_PATH + ".check_call"
        ) as mock_chk_call, mock.patch(
            SETUP_ERROR_PATH
        ) as mock_error:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_writer.side_effect = mock_file_writer
            mock_error.side_effect = mock_return_args

            def _check_exception_behavior(exception):
                mock_chk_call.side_effect = exception

                self.assertTrue(self.setup_task.side_pane.ui_enabled)
                self.assertTrue(self.setup_task.setup_pane.ui_enabled)

                with self.event_loop_until_condition(
                    lambda: mock_chk_call.called
                ):
                    self.setup_task.run_bdss()

                ui_enabled = self.setup_task.side_pane.ui_enabled
                with self.event_loop_until_condition(lambda: ui_enabled):
                    pass

                ui_enabled = self.setup_task.setup_pane.ui_enabled
                with self.event_loop_until_condition(lambda: ui_enabled):
                    pass

                return mock_error.call_args[0][1]

            msg = "boom"
            exc = Exception(msg)
            self.assertTrue(
                _check_exception_behavior(exc).startswith(
                    "Execution of BDSS failed. \n\n" + msg
                )
            )
            msg = "whatever"
            exc = OSError(msg)
            self.assertTrue(
                _check_exception_behavior(exc).startswith(
                    "Execution of BDSS failed. \n\n" + msg
                )
            )

    def test__execute_bdss_failure(self):
        with mock.patch("subprocess.check_call") as mock_call:
            mock_call.side_effect = subprocess.CalledProcessError(
                1, "fake_command"
            )
            with LogCapture() as capture:
                with self.assertRaises(subprocess.CalledProcessError):
                    self.setup_task._execute_bdss("")
            capture.check(
                (
                    "force_wfmanager.wfmanager_setup_task",
                    "ERROR",
                    "force_bdss returned a non-zero value after execution",
                ),
                (
                    "force_wfmanager.wfmanager_setup_task",
                    "ERROR",
                    "Unable to delete temporary workflow file at ",
                ),
            )

    def test_run_bdss_write_failure(self):
        with mock.patch(WORKFLOW_WRITER_PATH) as mock_writer, mock.patch(
            SETUP_ERROR_PATH
        ) as mock_error:
            workflow_writer = mock.Mock(spec=WorkflowWriter)
            workflow_writer.write.side_effect = Exception("write failed")
            mock_writer.return_value = workflow_writer
            mock_error.side_effect = mock_return_args

            self.assertTrue(self.setup_task.side_pane.ui_enabled)
            self.assertTrue(self.setup_task.setup_pane.ui_enabled)

            self.setup_task.run_bdss()

            self.assertTrue(self.setup_task.side_pane.ui_enabled)
            self.assertTrue(self.setup_task.setup_pane.ui_enabled)

            self.assertEqual(
                mock_error.call_args[0][1], "Unable to run BDSS: write failed"
            )

    def test_ui_select(self):

        contributed_ui = DummyContributedUI2()

        class MockUIModal:
            def __init__(self, **kwargs):
                self.selected_ui = contributed_ui

            def edit_traits(self):
                pass

        ui_wfmanager = DummyUIWfManager()
        # Get a reference to the plugins we expect to use in the modal dialog
        ui_plugin = ui_wfmanager.get_plugin(
            plugin_id("enthought", "uitest", 2)
        )
        ui_plugin_old = ui_wfmanager.get_plugin(
            plugin_id("enthought", "uitest", 1)
        )
        setup_task, _ = get_probe_wfmanager_tasks(
            wf_manager=ui_wfmanager, contributed_uis=[contributed_ui]
        )

        with mock.patch(UI_SELECT_MODAL_PATH) as mock_ui_modal:
            mock_ui_modal.side_effect = MockUIModal
            setup_task.ui_select()
        # Check the plugins were sorted
        mock_ui_modal.assert_called_with(
            available_plugins=[ui_plugin_old, ui_plugin],
            contributed_uis=[contributed_ui],
        )
        # Press the 'update workflow' button
        with self.assertTraitChanges(setup_task, "workflow_model"):
            setup_task.selected_contributed_ui.update_workflow = True

        # Press the 'run simulation' button
        with mock.patch(RUN_BDSS_PATH) as _mock_run:
            with self.assertTraitChanges(setup_task, "workflow_model"):
                setup_task.selected_contributed_ui.run_workflow = True
        _mock_run.assert_called()

    def test_control_buttons(self):
        with mock.patch(
            "force_wfmanager.server.zmq_server.ZMQServer.publish_message"
        ) as mock_publish:
            self.setup_task.stop_bdss()
            self.assertFalse(self.setup_task._paused)
            self.assertTrue(self.setup_task._not_paused)
            mock_publish.assert_called_with("STOP_BDSS")

            self.setup_task.pause_bdss()
            self.assertTrue(self.setup_task._paused)
            self.assertFalse(self.setup_task._not_paused)
            mock_publish.assert_called_with("PAUSE_BDSS")

            self.setup_task.pause_bdss()
            self.assertFalse(self.setup_task._paused)
            self.assertTrue(self.setup_task._not_paused)
            mock_publish.assert_called_with("RESUME_BDSS")

        with mock.patch.object(self.setup_task, "run_bdss") as mock_run:
            self.setup_task.run_button_clicked()
            mock_run.assert_called()

    def test__bdss_done(self):
        with mock.patch(
            "force_wfmanager.wfmanager_setup_task.information"
        ) as mock_info:
            exception = subprocess.SubprocessError()
            self.setup_task._bdss_done(exception)
            mock_info.assert_called_with(
                None, "Execution of BDSS stopped by the user."
            )
