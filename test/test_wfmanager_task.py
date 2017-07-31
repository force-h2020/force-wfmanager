import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from envisage.plugin import Plugin

from pyface.api import FileDialog, OK

from force_bdss.core_plugins.dummy.dummy_dakota.dakota_bundle import (
    DummyDakotaBundle)
from force_bdss.core_plugins.dummy.csv_extractor.csv_extractor_bundle import (
    CSVExtractorBundle)
from force_bdss.core_plugins.dummy.kpi_adder.kpi_adder_bundle import (
    KPIAdderBundle)
from force_bdss.io.workflow_writer import WorkflowWriter

from force_wfmanager.wfmanager_task import WfManagerTask


def get_wfmanager_task():
    plugin = mock.Mock(spec=Plugin)
    return WfManagerTask(
        mco_bundles=[DummyDakotaBundle(plugin)],
        data_source_bundles=[CSVExtractorBundle(plugin)],
        kpi_calculator_bundles=[KPIAdderBundle(plugin)]
    )


class TestWFManagerTask(unittest.TestCase):
    def setUp(self):
        self.wfmanager_task = get_wfmanager_task()

    def test_save_workflow(self):
        def mock_file_dialog(*args, **kwargs):
            file_dialog = mock.Mock(spec=FileDialog)
            file_dialog.open = lambda: OK
            file_dialog.path = ''
            return file_dialog

        def mock_file_open(*args, **kwargs):
            return ''

        def mock_file_writer(*args, **kwargs):
            def write(*args, **kwargs):
                return ''
            writer = mock.Mock(spec=WorkflowWriter)
            writer.write = write
            return writer

        file_dialog_path = 'force_wfmanager.wfmanager_task.FileDialog'
        file_open_path = 'force_wfmanager.wfmanager_task.open'
        workflow_writer_path = 'force_wfmanager.wfmanager_task.WorkflowWriter'
        with mock.patch(file_dialog_path) as mock_dialog, \
                mock.patch(file_open_path) as mock_open, \
                mock.patch(workflow_writer_path) as mock_writer:
            mock_dialog.side_effect = mock_file_dialog
            mock_file_open.side_effect = mock_open
            mock_writer.side_effect = mock_file_writer
            self.wfmanager_task.save_workflow()
