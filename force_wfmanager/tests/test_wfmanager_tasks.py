import unittest
import subprocess

from unittest import mock

from force_bdss.core.data_value import DataValue
from force_bdss.io.workflow_reader import WorkflowReader, InvalidFileException
from force_bdss.io.workflow_writer import WorkflowWriter
from force_wfmanager.central_pane.graph_pane import GraphPane
from force_wfmanager.central_pane.setup_pane import SetupPane
from force_wfmanager.server.zmq_server import ZMQServer
from force_wfmanager.tests.utils import wait_condition
from pyface.constant import OK, CANCEL, YES
from pyface.file_dialog import FileDialog
from pyface.tasks.api import TaskWindow

from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant

from force_bdss.tests.probe_classes.factory_registry_plugin import \
    ProbeFactoryRegistryPlugin
from force_bdss.api import Workflow, MCOProgressEvent, MCOStartEvent

from force_wfmanager.wfmanager import WfManager
from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask
from force_wfmanager.wfmanager_results_task import WfManagerResultsTask
from force_wfmanager.left_side_pane.tree_pane import TreePane
from force_wfmanager.left_side_pane.results_pane import ResultsPane
from force_wfmanager.central_pane.analysis_model import AnalysisModel

from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin
from testfixtures import LogCapture

CONFIRMATION_DIALOG_PATH = \
    'force_wfmanager.wfmanager_setup_task.ConfirmationDialog'
FILE_DIALOG_PATH = 'force_wfmanager.wfmanager_setup_task.FileDialog'
INFORMATION_PATH = 'force_wfmanager.wfmanager_setup_task.information'
CONFIRM_PATH = 'force_wfmanager.wfmanager_setup_task.confirm'
FILE_OPEN_PATH = 'force_wfmanager.wfmanager_setup_task.open'
WORKFLOW_WRITER_PATH = 'force_wfmanager.wfmanager_setup_task.WorkflowWriter'
WORKFLOW_READER_PATH = 'force_wfmanager.wfmanager_setup_task.WorkflowReader'
ERROR_PATH = 'force_wfmanager.wfmanager_setup_task.error'
SUBPROCESS_PATH = 'force_wfmanager.wfmanager_setup_task.subprocess'
OS_REMOVE_PATH = 'force_wfmanager.wfmanager_setup_task.os.remove'
ZMQSERVER_SETUP_SOCKETS_PATH = \
    'force_wfmanager.wfmanager_setup_task.ZMQServer._setup_sockets'


def mock_dialog(dialog_class, result, path=''):
    def mock_dialog_call(*args, **kwargs):
        dialog = mock.Mock(spec=dialog_class)
        dialog.open = lambda: result
        dialog.path = path
        return dialog
    return mock_dialog_call


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


def mock_file_reader(*args, **kwargs):
    def read(*args, **kwargs):
        workflow = Workflow()
        return workflow
    reader = mock.Mock(spec=WorkflowReader)
    reader.read = read
    return reader


def mock_file_reader_failure(*args, **kwargs):
    def read(*args, **kwargs):
        raise InvalidFileException("OUPS")
    reader = mock.Mock(spec=WorkflowReader)
    reader.read = read
    return reader


def mock_os_remove(*args, **kwargs):
    raise OSError("OUPS")


def mock_show_error(*args, **kwargs):
    return args


def mock_subprocess(*args, **kwargs):
    def check_call(*args, **kwargs):
        return
    mock_subprocess_module = mock.Mock(spec=subprocess)
    mock_subprocess_module.check_call = check_call
    return mock_subprocess_module


def mock_info_dialog(*args, **kwargs):
    return args


def get_wfmanager_tasks():
    # Returns the Setup and Results Tasks, with a mock TaskWindow and dummy
    # Application which does not have an event loop.
    app = dummy_wfmanager()
    analysis_m = AnalysisModel()
    workflow_m = Workflow()
    factory_registry_plugin = ProbeFactoryRegistryPlugin()
    setup_task = WfManagerSetupTask(
        analysis_m=analysis_m, workflow_m=workflow_m,
        factory_registry=factory_registry_plugin
    )
    results_task = WfManagerResultsTask(
        analysis_m=analysis_m, workflow_m=workflow_m,
        factory_registry=factory_registry_plugin
    )
    tasks = [setup_task, results_task]

    for task in tasks:
        mock_window = mock.Mock(spec=TaskWindow)
        mock_window.tasks = tasks
        task.window = mock_window
        task.window.application = app
        task.window.application.factory_registry = factory_registry_plugin

        task.create_central_pane()
        task.create_dock_panes()

    return tasks[0], tasks[1]


def dummy_wfmanager():
    plugins = [CorePlugin(), TasksPlugin()]
    wfmanager = WfManager(plugins=plugins)
    wfmanager.run = lambda: None
    return wfmanager


class TestWFManagerTasks(GuiTestAssistant, unittest.TestCase):
    def setUp(self):
        super(TestWFManagerTasks, self).setUp()
        self.setup_task, self.results_task = get_wfmanager_tasks()

    def test_init(self):
        self.assertIsInstance(self.setup_task.create_central_pane(),
                              SetupPane)
        self.assertEqual(len(self.setup_task.create_dock_panes()), 1)
        self.assertIsInstance(self.setup_task.side_pane, TreePane)

        self.assertEqual(len(self.results_task.create_dock_panes()),
                         1)
        self.assertIsInstance(self.results_task.side_pane,
                              ResultsPane)
        self.assertIsInstance(self.results_task.create_central_pane(),
                              GraphPane)

    def test_zmq_start(self):
        self.setup_task.zmq_server = mock.Mock(spec=ZMQServer)
        self.setup_task.initialized()
        self.assertTrue(self.setup_task.zmq_server.start.called)

    def test_failed_initialization_of_ui_hooks(self):
        plugin = ProbeFactoryRegistryPlugin()

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
                mock.patch(ERROR_PATH) as mock_error:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_error.side_effect = mock_show_error

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
            mock_information.side_effect = mock_info_dialog

            self.setup_task.open_about()

            self.assertTrue(mock_information.called)

    def test_open_failure(self):
        mock_open = mock.mock_open()
        mock_open.side_effect = IOError("OUPS")
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(ERROR_PATH) as mock_error:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_error.side_effect = mock_show_error

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
            old_workflow = self.setup_task.workflow_m
            self.assertEqual(
                old_workflow,
                self.setup_task.workflow_m)
            self.assertEqual(
                old_workflow,
                self.setup_task.side_pane.workflow_tree.model)

            self.setup_task.open_workflow()

            self.assertTrue(mock_open.called)
            self.assertTrue(mock_reader.called)

            self.assertNotEqual(old_workflow, self.setup_task.workflow_m)
            self.assertNotEqual(
                old_workflow,
                self.setup_task.workflow_m)
            self.assertNotEqual(
               old_workflow,
               self.setup_task.side_pane.workflow_tree.model)

    def test_read_failure(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(ERROR_PATH) as mock_error, \
                mock.patch(WORKFLOW_READER_PATH) as mock_reader:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_error.side_effect = mock_show_error
            mock_reader.side_effect = mock_file_reader_failure

            old_workflow = self.setup_task.workflow_m

            self.setup_task.open_workflow()

            self.assertTrue(mock_open.called)
            self.assertTrue(mock_reader.called)
            mock_error.assert_called_with(
                None,
                'Cannot read the requested file:\n\nOUPS',
                'Error when reading file'
            )
            self.assertEqual(old_workflow, self.setup_task.workflow_m)

    def test_dispatch_mco_event(self):
        send_event = self.setup_task._server_event_callback
        self.assertEqual(self.setup_task.analysis_m.value_names, ())
        with self.event_loop():
            send_event(MCOStartEvent(
                parameter_names=["x"],
                kpi_names=["y"])
            )

        self.assertEqual(
            len(self.setup_task.analysis_m.evaluation_steps),
            0)
        self.assertEqual(
            self.setup_task.analysis_m.value_names,
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
            len(self.setup_task.analysis_m.evaluation_steps),
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
                mock.patch(ERROR_PATH) as mock_error, \
                self.event_loop_until_condition(lambda: mock_error.called):

            setup_sockets.side_effect = Exception("boom")
            self.setup_task.zmq_server.start()

    def test_open_plugin_dialog(self):

        with self.event_loop():
            self.setup_task.open_plugins()

    def test_run_bdss(self):

        self.setup_task.analysis_m.value_names = ('x', )
        self.setup_task.analysis_m.add_evaluation_step((2.0, ))
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
        self.setup_task.analysis_m.value_names = ('x', )
        self.setup_task.analysis_m.add_evaluation_step((2.0, ))
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

                self.assertTrue(self.setup_task.side_pane.ui_enabled)

                with self.event_loop_until_condition(
                        lambda: mock_check_call.called):
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
                        "Execution of BDSS failed. \n\n"+msg))

    def test_run_bdss_write_failure(self):
        with mock.patch(WORKFLOW_WRITER_PATH) as mock_writer, \
                mock.patch(ERROR_PATH) as mock_error:
            workflow_writer = mock.Mock(spec=WorkflowWriter)
            workflow_writer.write.side_effect = Exception("write failed")
            mock_writer.return_value = workflow_writer
            mock_error.side_effect = mock_show_error

            self.assertTrue(self.setup_task.side_pane.ui_enabled)

            self.setup_task.run_bdss()

            self.assertTrue(self.setup_task.side_pane.ui_enabled)

            self.assertEqual(
                mock_error.call_args[0][1],
                'Unable to run BDSS: write failed')
