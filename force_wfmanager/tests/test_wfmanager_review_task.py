from unittest import mock, TestCase

from pyface.constant import OK
from pyface.file_dialog import FileDialog
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant

from .mock_methods import (
    mock_file_writer, mock_dialog, mock_return_args
)
from .test_wfmanager_tasks import get_probe_wfmanager_tasks


RESULTS_FILE_DIALOG_PATH = 'force_wfmanager.wfmanager_review_task.FileDialog'
RESULTS_FILE_OPEN_PATH = 'force_wfmanager.io.project_io.open'
RESULTS_JSON_DUMP_PATH = 'force_wfmanager.io.project_io.json.dump'
RESULTS_WRITER_PATH = \
    'force_wfmanager.io.project_io.WorkflowWriter.get_workflow_data'
RESULTS_ERROR_PATH = 'force_wfmanager.wfmanager_review_task.error'


class TestWFManagerTasks(GuiTestAssistant, TestCase):
    def setUp(self):
        super(TestWFManagerTasks, self).setUp()
        _, self.review_task = get_probe_wfmanager_tasks()

    def test_save_project(self):
        mock_open = mock.mock_open()
        with mock.patch(RESULTS_FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(RESULTS_JSON_DUMP_PATH) as mock_json_dump, \
                mock.patch(RESULTS_FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(RESULTS_WRITER_PATH) as mock_wf_writer:
            mock_file_dialog.side_effect = mock_dialog(
                FileDialog, OK, 'file_path')
            mock_wf_writer.side_effect = mock_file_writer

            self.review_task.save_project_as()

            self.assertTrue(mock_wf_writer.called)
            self.assertTrue(mock_open.called)
            self.assertTrue(mock_json_dump.called)
            self.assertTrue(mock_file_dialog.called)

    def test_save_project_failure(self):
        mock_open = mock.mock_open()
        mock_open.side_effect = IOError("OUPS")
        with mock.patch(RESULTS_FILE_DIALOG_PATH) as mock_file_dialog, \
                mock.patch(RESULTS_FILE_OPEN_PATH, mock_open, create=True), \
                mock.patch(RESULTS_ERROR_PATH) as mock_error:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_error.side_effect = mock_return_args

            self.review_task.save_project_as()

            self.assertTrue(mock_open.called)
            mock_error.assert_called_with(
                None,
                'Cannot save in the requested file:\n\nOUPS',
                'Error when saving the project'
            )
