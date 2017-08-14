import unittest
try:
    import mock
except ImportError:
    from unittest import mock
import subprocess

from pyface.tasks.api import TaskLayout

from pyface.api import FileDialog, OK

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

from force_wfmanager.wfmanager_task import WfManagerTask, cleanup_garbage
from force_wfmanager.left_side_pane.side_pane import SidePane
from force_wfmanager.left_side_pane.workflow_settings import WorkflowSettings

FILE_DIALOG_PATH = 'force_wfmanager.wfmanager_task.FileDialog'
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

    wfmanager_task.create_central_pane()
    wfmanager_task.create_dock_panes()
    return wfmanager_task


def mock_file_dialog(*args, **kwargs):
    file_dialog = mock.Mock(spec=FileDialog)
    file_dialog.open = lambda: OK
    file_dialog.path = 'file_path'
    return file_dialog


def mock_file_dialog_being_closed(*args, **kwargs):
    file_dialog = mock.Mock(spec=FileDialog)
    file_dialog.open = lambda: False
    file_dialog.path = ''
    return file_dialog


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


class TestWFManagerTask(unittest.TestCase):
    def setUp(self):
        self.wfmanager_task = get_wfmanager_task()

    def test_init(self):
        self.assertEqual(len(self.wfmanager_task.create_dock_panes()), 1)
        self.assertIsInstance(self.wfmanager_task.side_pane, SidePane)
        self.assertIsInstance(
            self.wfmanager_task.side_pane.workflow_settings, WorkflowSettings)
        self.assertIsInstance(self.wfmanager_task.default_layout, TaskLayout)

    def test_save_workflow(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer:
            mock_dialog.side_effect = mock_file_dialog
            mock_writer.side_effect = mock_file_writer

            self.wfmanager_task.save_workflow()
            mock_writer.assert_called()
            mock_open.assert_called()
            mock_dialog.assert_called()

            self.assertEqual(
                self.wfmanager_task.current_file,
                'file_path'
            )

        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer:
            mock_dialog.side_effect = mock_file_dialog
            mock_writer.side_effect = mock_file_writer

            self.wfmanager_task.save_workflow()
            mock_writer.assert_called()
            mock_open.assert_called()
            mock_dialog.assert_not_called()

    def test_close_saving_dialog(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer:
            mock_dialog.side_effect = mock_file_dialog_being_closed
            mock_writer.side_effect = mock_file_writer

            self.wfmanager_task.save_workflow()
            mock_open.assert_not_called()

    def test_open_workflow(self):
        mock_open = mock.mock_open()
        with mock.patch(FILE_DIALOG_PATH) as mock_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_READER_PATH) as mock_reader:
            mock_dialog.side_effect = mock_file_dialog
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
        with mock.patch(FILE_DIALOG_PATH) as mock_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(ERROR_PATH) as mock_error, \
                mock.patch(WORKFLOW_READER_PATH) as mock_reader:
            mock_dialog.side_effect = mock_file_dialog
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
        with mock.patch(FILE_DIALOG_PATH) as mock_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(WORKFLOW_WRITER_PATH) as mock_writer, \
                mock.patch(SUBPROCESS_PATH) as _mock_subprocess:
            mock_dialog.side_effect = mock_file_dialog
            mock_writer.side_effect = mock_file_writer
            _mock_subprocess.side_effect = mock_subprocess

            self.wfmanager_task.run_bdss()
            mock_writer.assert_called()
            _mock_subprocess.check_call.assert_called()

    def test_cleanup_garbage(self):
        with mock.patch(OS_REMOVE_PATH) as mock_os:
            mock_os.side_effect = mock_os_remove

            with self.assertRaises(OSError):
                with cleanup_garbage('wrongFile'):
                    pass

    def test_open_failure(self):
        mock_open = mock.mock_open()
        mock_open.side_effect = IOError("OUPS")
        with mock.patch(FILE_DIALOG_PATH) as mock_dialog, \
                mock.patch(FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(ERROR_PATH) as mock_error:
            mock_dialog.side_effect = mock_file_dialog
            mock_error.side_effect = mock_show_error

            self.wfmanager_task.save_workflow()
            mock_open.assert_called()
            mock_error.assert_called_with(
                None,
                'Cannot save in the requested file:\n\nOUPS',
                'Error when saving workflow'
            )