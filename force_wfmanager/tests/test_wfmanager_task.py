import unittest

from force_wfmanager.central_pane.analysis_model import AnalysisModel

try:
    import mock
except ImportError:
    from unittest import mock
import subprocess

from envisage.api import Application

from pyface.tasks.api import TaskLayout, TaskWindow
from pyface.api import FileDialog, OK, ConfirmationDialog, YES, NO, CANCEL
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant


from force_bdss.core_plugins.dummy.dummy_dakota.dakota_factory import (
    DummyDakotaFactory)
from force_bdss.core_plugins.dummy.csv_extractor.csv_extractor_factory import (
    CSVExtractorFactory)
from force_bdss.core_plugins.dummy.kpi_adder.kpi_adder_factory import (
    KPIAdderFactory)
from force_bdss.factory_registry_plugin import FactoryRegistryPlugin
from force_bdss.core.workflow import Workflow
from force_bdss.io.workflow_writer import WorkflowWriter
from force_bdss.io.workflow_reader import WorkflowReader, InvalidFileException

from force_wfmanager.wfmanager_task import WfManagerTask
from force_wfmanager.left_side_pane.side_pane import SidePane
from force_wfmanager.left_side_pane.workflow_settings import WorkflowSettings

FILE_DIALOG_PATH = 'force_wfmanager.wfmanager_task.FileDialog'
CONFIRMATION_DIALOG_PATH = 'force_wfmanager.wfmanager_task.ConfirmationDialog'
FILE_OPEN_PATH = 'force_wfmanager.wfmanager_task.open'
WORKFLOW_WRITER_PATH = 'force_wfmanager.wfmanager_task.WorkflowWriter'
WORKFLOW_READER_PATH = 'force_wfmanager.wfmanager_task.WorkflowReader'
ERROR_PATH = 'force_wfmanager.wfmanager_task.error'
SUBPROCESS_PATH = 'force_wfmanager.wfmanager_task.subprocess'
OS_REMOVE_PATH = 'force_wfmanager.wfmanager_task.os.remove'


def get_wfmanager_task():
    mock_plugin = mock.Mock(spec=FactoryRegistryPlugin)
    mock_plugin.mco_factories = [mock.Mock(spec=DummyDakotaFactory)]
    mock_plugin.data_source_factories = [mock.Mock(spec=CSVExtractorFactory)]
    mock_plugin.kpi_calculator_factories = [mock.Mock(spec=KPIAdderFactory)]
    wfmanager_task = WfManagerTask(factory_registry=mock_plugin)

    wfmanager_task.window = mock.Mock(spec=TaskWindow)
    wfmanager_task.window.application = mock.Mock(spec=Application)
    wfmanager_task.window.application.exit = mock.Mock()

    wfmanager_task.create_central_pane()
    wfmanager_task.create_dock_panes()

    return wfmanager_task


def mock_dialog(dialog_class, result, path=''):
    def mock_dialog_call(*args, **kwargs):
        dialog = mock.Mock(spec=dialog_class)
        dialog.open = lambda: result
        dialog.path = path
        return dialog
    return mock_dialog_call


def mock_os_remove(*args, **kwargs):
    raise OSError("OUPS")


def mock_show_error(*args, **kwargs):
    return args


def mock_file_writer(*args, **kwargs):
    def write(*args, **kwargs):
        return ''
    writer = mock.Mock(spec=WorkflowWriter)
    writer.write = write
    return writer


def mock_file_reader(*args, **kwargs):
    def read(*args, **kwargs):
        return mock.Mock(spec=Workflow)
    reader = mock.Mock(spec=WorkflowReader)
    reader.read = read
    return reader


def mock_file_reader_failure(*args, **kwargs):
    def read(*args, **kwargs):
        raise InvalidFileException("OUPS")
    reader = mock.Mock(spec=WorkflowReader)
    reader.read = read
    return reader


def mock_subprocess(*args, **kwargs):
    def check_call(*args, **kwargs):
        return
    mock_subprocess_module = mock.Mock(spec=subprocess)
    mock_subprocess_module.check_call = check_call
    return mock_subprocess_module


class TestWFManagerTask(GuiTestAssistant, unittest.TestCase):
    def setUp(self):
        super(TestWFManagerTask, self).setUp()
        self.wfmanager_task = get_wfmanager_task()

    def test_init(self):
        self.assertEqual(len(self.wfmanager_task.create_dock_panes()), 1)
        self.assertIsInstance(self.wfmanager_task.side_pane, SidePane)
        self.assertIsInstance(
            self.wfmanager_task.side_pane.workflow_settings, WorkflowSettings)
        self.assertIsInstance(self.wfmanager_task.default_layout, TaskLayout)
        self.assertIsInstance(self.wfmanager_task.analysis_m, AnalysisModel)

    def test_save_workflow(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer:
            mock_file_dialog.side_effect = mock_dialog(
                FileDialog, OK, 'file_path')
            mock_writer.side_effect = mock_file_writer

            self.wfmanager_task.save_workflow()

            mock_writer.assert_called()
            mock_open.assert_called()
            mock_file_dialog.assert_called()

            self.assertEqual(
                self.wfmanager_task.current_file,
                'file_path'
            )

        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_writer.side_effect = mock_file_writer

            self.wfmanager_task.save_workflow()

            mock_writer.assert_called()
            mock_open.assert_called()
            mock_file_dialog.assert_not_called()

    def test_save_workflow_failure(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer:
            mock_file_dialog.side_effect = mock_dialog(
                FileDialog, OK, 'file_path')
            mock_writer.side_effect = mock_file_writer

            self.wfmanager_task.save_workflow()

            self.assertEqual(
                self.wfmanager_task.current_file,
                'file_path'
            )

        mock_open = mock.mock_open()
        mock_open.side_effect = Exception("OUPS")
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(ERROR_PATH) as mock_error:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_error.side_effect = mock_show_error

            self.wfmanager_task.save_workflow()

            self.assertEqual(
                self.wfmanager_task.current_file,
                ''
            )

            mock_error.assert_called()

    def test_close_saving_dialog(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, CANCEL)
            mock_writer.side_effect = mock_file_writer

            self.wfmanager_task.save_workflow_as()
            mock_open.assert_not_called()

    def test_open_failure(self):
        mock_open = mock.mock_open()
        mock_open.side_effect = IOError("OUPS")
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(ERROR_PATH) as mock_error:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_error.side_effect = mock_show_error

            self.wfmanager_task.save_workflow_as()

            mock_open.assert_called()
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

            old_workflow = self.wfmanager_task.workflow_m
            self.assertEqual(
                old_workflow,
                self.wfmanager_task.side_pane.workflow_m)
            self.assertEqual(
                old_workflow,
                self.wfmanager_task.side_pane.workflow_settings.workflow_m)

            self.wfmanager_task.open_workflow()

            mock_open.assert_called()
            mock_reader.assert_called()

            self.assertNotEqual(old_workflow, self.wfmanager_task.workflow_m)
            self.assertNotEqual(
                old_workflow,
                self.wfmanager_task.side_pane.workflow_m)
            self.assertNotEqual(
                old_workflow,
                self.wfmanager_task.side_pane.workflow_settings.workflow_m)

    def test_read_failure(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(ERROR_PATH) as mock_error, \
                mock.patch(WORKFLOW_READER_PATH) as mock_reader:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_error.side_effect = mock_show_error
            mock_reader.side_effect = mock_file_reader_failure

            old_workflow = self.wfmanager_task.workflow_m

            self.wfmanager_task.open_workflow()

            mock_open.assert_called()
            mock_reader.assert_called()
            mock_error.assert_called_with(
                None,
                'Cannot read the requested file:\n\nOUPS',
                'Error when reading file'
            )
            self.assertEqual(old_workflow, self.wfmanager_task.workflow_m)

    def test_run_bdss(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer, \
                mock.patch(SUBPROCESS_PATH) as _mock_subprocess:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_writer.side_effect = mock_file_writer
            mock_subprocess.side_effect = mock_subprocess

            self.assertTrue(self.wfmanager_task.side_pane.enabled)

            with self.event_loop_until_condition(
                    lambda: _mock_subprocess.check_call.called):
                self.wfmanager_task.run_bdss()

            with self.event_loop_until_condition(
                    lambda: self.wfmanager_task.side_pane.enabled):
                pass

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

                self.assertTrue(self.wfmanager_task.side_pane.enabled)

                with self.event_loop_until_condition(
                        lambda: mock_check_call.called):
                    self.wfmanager_task.run_bdss()

                with self.event_loop_until_condition(
                        lambda: self.wfmanager_task.side_pane.enabled):
                    pass

                return mock_error.call_args[0][1]

            for exc, msg in [
                    (Exception("boom"), 'boom'),
                    (subprocess.CalledProcessError(1, "fake_command"),
                        "Command 'fake_command' returned non-zero exit "
                        "status 1"),
                    (OSError("whatever"), "whatever")]:
                self.assertEqual(
                    _check_exception_behavior(exc),
                    "Execution of BDSS failed. \n\n"+msg)

    def test_run_bdss_write_failure(self):
        with mock.patch(WORKFLOW_WRITER_PATH) as mock_writer, \
                mock.patch(ERROR_PATH) as mock_error:
            workflow_writer = mock.Mock(spec=WorkflowWriter)
            workflow_writer.write.side_effect = Exception("write failed")
            mock_writer.return_value = workflow_writer
            mock_error.side_effect = mock_show_error

            self.assertTrue(self.wfmanager_task.side_pane.enabled)

            with self.event_loop_until_condition(
                    lambda: self.wfmanager_task.side_pane.enabled):
                self.wfmanager_task.run_bdss()

            self.assertEqual(
                mock_error.call_args[0][1],
                'Unable to create temporary workflow file for execution'
                ' of the BDSS. write failed')

    def test_exit_application_with_saving(self):
        mock_open = mock.mock_open()
        with mock.patch(CONFIRMATION_DIALOG_PATH) as mock_confirm_dialog, \
                mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer:
            mock_confirm_dialog.side_effect = mock_dialog(
                ConfirmationDialog, YES)
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_writer.side_effect = mock_file_writer

            self.wfmanager_task.exit()

            mock_confirm_dialog.assert_called()
            mock_file_dialog.assert_called()
            mock_open.assert_called()
            mock_writer.assert_called()
            self.wfmanager_task.window.application.exit.assert_called()

    def test_exit_application_with_saving_failure(self):
        mock_open = mock.mock_open()
        mock_open.side_effect = Exception("OUPS")
        with mock.patch(CONFIRMATION_DIALOG_PATH) as mock_confirm_dialog, \
                mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(ERROR_PATH) as mock_error, \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer:
            mock_confirm_dialog.side_effect = mock_dialog(
                ConfirmationDialog, YES)
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_error.side_effect = mock_show_error
            mock_writer.side_effect = mock_file_writer

            self.wfmanager_task.exit()

            mock_confirm_dialog.assert_called()
            mock_file_dialog.assert_called()
            mock_open.assert_called()
            mock_writer.write.assert_not_called()
            self.wfmanager_task.window.application.exit.assert_not_called()

    def test_exit_application_without_saving(self):
        mock_open = mock.mock_open()
        with mock.patch(CONFIRMATION_DIALOG_PATH) as mock_confirm_dialog, \
                mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer:
            mock_confirm_dialog.side_effect = mock_dialog(
                ConfirmationDialog, NO)
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_writer.side_effect = mock_file_writer

            self.wfmanager_task.exit()

            mock_confirm_dialog.assert_called()
            mock_file_dialog.assert_not_called()
            mock_open.assert_not_called()
            mock_writer.write.assert_not_called()
            self.wfmanager_task.window.application.exit.assert_called()

    def test_cancel_exit_application(self):
        mock_open = mock.mock_open()
        with mock.patch(CONFIRMATION_DIALOG_PATH) as mock_confirm_dialog, \
                mock.patch(FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer:
            mock_confirm_dialog.side_effect = mock_dialog(
                ConfirmationDialog, CANCEL)
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_writer.side_effect = mock_file_writer

            self.wfmanager_task.exit()

            mock_confirm_dialog.assert_called()
            mock_file_dialog.assert_not_called()
            mock_open.assert_not_called()
            mock_writer.write.assert_not_called()
            self.wfmanager_task.window.application.exit.assert_not_called()

    def test_dispatch_mco_event(self):
        pass
