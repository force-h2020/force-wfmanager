import unittest
import unittest.mock as mock

from testfixtures import LogCapture

from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin

from pyface.api import (ConfirmationDialog, YES, NO, CANCEL, FileDialog, OK)
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant


from force_wfmanager.wfmanager_plugin import WfManagerPlugin
from force_wfmanager.wfmanager import WfManager, TaskWindowClosePrompt
from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask
from force_wfmanager.wfmanager_results_task import WfManagerResultsTask

from force_wfmanager.central_pane.analysis_model import AnalysisModel
from force_bdss.tests.probe_classes.factory_registry_plugin import (
    ProbeFactoryRegistryPlugin
)

from force_bdss.api import (MCOStartEvent, MCOProgressEvent, Workflow,
                            WorkflowWriter, WorkflowReader,
                            InvalidFileException, DataValue)

from force_wfmanager.server.zmq_server import ZMQServer
from force_wfmanager.tests.utils import wait_condition

CONFIRMATION_DIALOG_PATH = 'force_wfmanager.wfmanager.ConfirmationDialog'
FILE_DIALOG_PATH = 'force_wfmanager.wfmanager.FileDialog'
INFORMATION_PATH = 'force_wfmanager.wfmanager.information'
CONFIRM_PATH = 'force_wfmanager.wfmanager.confirm'
FILE_OPEN_PATH = 'force_wfmanager.wfmanager.open'
WORKFLOW_WRITER_PATH = 'force_wfmanager.wfmanager.WorkflowWriter'
WORKFLOW_READER_PATH = 'force_wfmanager.wfmanager.WorkflowReader'
ERROR_PATH = 'force_wfmanager.wfmanager.error'
SUBPROCESS_PATH = 'force_wfmanager.wfmanager.subprocess'
OS_REMOVE_PATH = 'force_wfmanager.wfmanager.os.remove'
ZMQSERVER_SETUP_SOCKETS_PATH = \
    'force_wfmanager.wfmanager.ZMQServer._setup_sockets'


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


def mock_info_dialog(*args, **kwargs):
    return args


def dummy_wfmanager():

    plugins = [CorePlugin(), TasksPlugin(), WfManagerPlugin()]
    wfmanager = WfManager(plugins=plugins, workflow_file=None)
    wfmanager.run = wfmanager._create_windows
    wfmanager.factory_registry = ProbeFactoryRegistryPlugin()
    setup_task = WfManagerSetupTask(shared_menu_bar=None)
    setup_task.window = mock_window(wfmanager)
    results_task = WfManagerResultsTask(shared_menu_bar=None)
    results_task.window = mock_window(wfmanager)
    wfmanager.tasks = [setup_task, results_task]
    return wfmanager


def mock_window(wfmanager):
    window = mock.Mock(TaskWindowClosePrompt)
    window.application = wfmanager
    return window


class TestWfManager(GuiTestAssistant, unittest.TestCase):
    def setUp(self):
        super(TestWfManager, self).setUp()
        self.wfmanager = dummy_wfmanager()

    def test_init(self):
        self.assertEqual(len(self.wfmanager.default_layout), 1)
        self.assertEqual(len(self.wfmanager.task_factories), 2)
        self.assertIsInstance(self.wfmanager.analysis_m, AnalysisModel)
        self.assertIsInstance(self.wfmanager.workflow_m, Workflow)
        self.assertEqual(len(self.wfmanager.ui_hooks_managers), 1)

    def test_remove_tasks_on_application_exiting(self):
        self.wfmanager.run()
        self.assertEqual(len(self.wfmanager.windows[0].tasks), 2)
        self.wfmanager.application_exiting = True
        self.assertEqual(len(self.wfmanager.windows[0].tasks), 0)

    def test_failed_initialization_of_ui_hooks(self):
        plugin = ProbeFactoryRegistryPlugin()

        plugin.ui_hooks_factories[0].create_ui_hooks_manager_raises = True

        self.wfmanager.factory_registry = plugin

        with LogCapture() as capture:
            self.assertEqual(len(self.wfmanager.ui_hooks_managers), 0)

        capture.check(
            ('force_wfmanager.wfmanager',
             'ERROR',
             'Failed to create UI hook manager by factory ProbeUIHooksFactory')
        )

    def test_save_workflow(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer:

            hook_manager = self.wfmanager.ui_hooks_managers[0]
            self.assertFalse(hook_manager.before_save_called)

            mock_file_dialog.side_effect = mock_dialog(
                FileDialog, OK, 'file_path')
            mock_writer.side_effect = mock_file_writer

            self.wfmanager.save_workflow()

            self.assertTrue(mock_writer.called)
            self.assertTrue(mock_open.called)
            self.assertTrue(mock_file_dialog.called)

            self.assertEqual(self.wfmanager.current_file, 'file_path')
            self.assertTrue(hook_manager.before_save_called)

            hook_manager.before_save_raises = True
            with LogCapture() as capture:
                self.wfmanager.save_workflow()

            capture.check(('force_wfmanager.wfmanager',
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

            self.wfmanager.save_workflow()

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

            self.wfmanager.save_workflow()

            self.assertEqual(
                self.wfmanager.current_file,
                'file_path'
            )

        mock_open = mock.mock_open()
        mock_open.side_effect = Exception("OUPS")
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(ERROR_PATH) as mock_error:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_error.side_effect = mock_show_error

            self.wfmanager.save_workflow()

            self.assertEqual(
                self.wfmanager.current_file,
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

            self.wfmanager.save_workflow_as()
            mock_open.assert_not_called()

    def test_about_action(self):
        with mock.patch(INFORMATION_PATH) as mock_information:
            mock_information.side_effect = mock_info_dialog

            self.wfmanager.open_about()

            self.assertTrue(mock_information.called)

    def test_open_failure(self):
        mock_open = mock.mock_open()
        mock_open.side_effect = IOError("OUPS")
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(ERROR_PATH) as mock_error:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_error.side_effect = mock_show_error

            self.wfmanager.save_workflow_as()

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
            old_workflow = self.wfmanager.workflow_m
            self.assertEqual(
                old_workflow,
                self.wfmanager.workflow_m)
            self.assertEqual(
                old_workflow,
                self.wfmanager.tasks[0].side_pane.workflow_tree.model)

            self.wfmanager.open_workflow()

            self.assertTrue(mock_open.called)
            self.assertTrue(mock_reader.called)

            self.assertNotEqual(old_workflow, self.wfmanager.workflow_m)
            self.assertNotEqual(
                old_workflow,
                self.wfmanager.workflow_m)
            self.assertNotEqual(
                old_workflow,
                self.wfmanager.tasks[0].side_pane.workflow_tree.model)

    def test_read_failure(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(ERROR_PATH) as mock_error, \
                mock.patch(WORKFLOW_READER_PATH) as mock_reader:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_error.side_effect = mock_show_error
            mock_reader.side_effect = mock_file_reader_failure

            old_workflow = self.wfmanager.workflow_m

            self.wfmanager.open_workflow()

            self.assertTrue(mock_open.called)
            self.assertTrue(mock_reader.called)
            mock_error.assert_called_with(
                None,
                'Cannot read the requested file:\n\nOUPS',
                'Error when reading file'
            )
            self.assertEqual(old_workflow, self.wfmanager.workflow_m)

    def test_dispatch_mco_event(self):
        send_event = self.wfmanager._server_event_callback
        self.assertEqual(self.wfmanager.analysis_m.value_names, ())
        with self.event_loop():
            send_event(MCOStartEvent(
                parameter_names=["x"],
                kpi_names=["y"])
            )

        self.assertEqual(
            len(self.wfmanager.analysis_m.evaluation_steps),
            0)
        self.assertEqual(
            self.wfmanager.analysis_m.value_names,
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
            len(self.wfmanager.analysis_m.evaluation_steps),
            1)

    def test_initialize_finalize(self):
        self.wfmanager.zmq_server.start()
        wait_condition(
            lambda: (self.wfmanager.zmq_server.state ==
                     ZMQServer.STATE_WAITING))

        self.wfmanager.zmq_server.stop()

        self.assertEqual(
            self.wfmanager.zmq_server.state,
            ZMQServer.STATE_STOPPED)

    def test_zmq_server_failure(self):
        with mock.patch(ZMQSERVER_SETUP_SOCKETS_PATH) as setup_sockets, \
                mock.patch(ERROR_PATH) as mock_error, \
                self.event_loop_until_condition(lambda: mock_error.called):

            setup_sockets.side_effect = Exception("boom")
            self.wfmanager.zmq_server.start()

    def test_open_plugin_dialog(self):

        with self.event_loop():
            self.wfmanager.open_plugins()


class TestTaskWindowClosePrompt(unittest.TestCase):

    def setUp(self):
        super(TestTaskWindowClosePrompt, self).setUp()
        self.wfmanager = dummy_wfmanager()

    def test_exit_application_with_saving(self):
        self.wfmanager.save_workflow = mock.Mock(return_value=True)
        window = TaskWindowClosePrompt(tasks=self.wfmanager.tasks,
                                       application=self.wfmanager)
        with mock.patch(CONFIRMATION_DIALOG_PATH) as mock_confirm_dialog:
            mock_confirm_dialog.side_effect = mock_dialog(
                ConfirmationDialog, YES)
            close_result = window.close()
            self.assertTrue(self.wfmanager.save_workflow.called)
            self.assertTrue(close_result)

    def test_exit_application_with_saving_failure(self):
        self.wfmanager.save_workflow = mock.Mock(return_value=False)
        window = TaskWindowClosePrompt(tasks=self.wfmanager.tasks,
                                       application=self.wfmanager)
        with mock.patch(CONFIRMATION_DIALOG_PATH) as mock_confirm_dialog:
            mock_confirm_dialog.side_effect = mock_dialog(
                ConfirmationDialog, YES)
            close_result = window.close()
            self.assertTrue(self.wfmanager.save_workflow.called)
            self.assertFalse(close_result)

    def test_exit_application_without_saving(self):
        self.wfmanager.save_workflow = mock.Mock(return_value=True)
        window = TaskWindowClosePrompt(tasks=self.wfmanager.tasks,
                                       application=self.wfmanager)
        with mock.patch(CONFIRMATION_DIALOG_PATH) as mock_confirm_dialog:
            mock_confirm_dialog.side_effect = mock_dialog(
                ConfirmationDialog, NO)
            close_result = window.close()
            self.assertFalse(self.wfmanager.save_workflow.called)
            self.assertTrue(close_result)

    def test_cancel_exit_application(self):
        self.wfmanager.save_workflow = mock.Mock(return_value=True)
        window = TaskWindowClosePrompt(tasks=self.wfmanager.tasks,
                                       application=self.wfmanager)
        with mock.patch(CONFIRMATION_DIALOG_PATH) as mock_confirm_dialog:
            mock_confirm_dialog.side_effect = mock_dialog(
                ConfirmationDialog, CANCEL)
            close_result = window.close()
            self.assertFalse(self.wfmanager.save_workflow.called)
            self.assertFalse(close_result)
