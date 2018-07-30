import unittest
from unittest import mock

from envisage.api import Application

from force_wfmanager.wfmanager_plugin import WfManagerPlugin
from force_wfmanager.wfmanager_task import WfManagerTask


class TestWfManagerPlugin(unittest.TestCase):
    def setUp(self):
        self.wfmanager_plugin = WfManagerPlugin()
        self.wfmanager_plugin.application = mock.Mock(spec=Application)

        self.wfmanager_plugin_file = WfManagerPlugin(workflow_file='test')
        self.wfmanager_plugin_file.application = mock.Mock(spec=Application)
        self.wfmanager_plugin_file.application.get_plugin = lambda pl_id: None

    def test_init(self):
        self.assertEqual(len(self.wfmanager_plugin.tasks), 1)
        self.assertEqual(self.wfmanager_plugin.tasks[0].name,
                         "Workflow Manager")

        def mock_wfmanager_task_constructor(*args, **kwargs):
            return

        with mock.patch(
                "force_wfmanager.wfmanager_plugin"
                ".WfManagerTask") as mock_task:
            mock_task.side_effect = mock_wfmanager_task_constructor

            self.wfmanager_plugin._create_task()
            mock_task.assert_called()

    def test_file_load(self):

        def mock_wfmanager_task_constructor(*args, **kwargs):
            wfm_task = mock.Mock(spec=WfManagerTask)
            wfm_task.open_workflow_file = lambda: None
            return mock_task

        with mock.patch(
                "force_wfmanager.wfmanager_plugin"
                ".WfManagerTask") as mock_task:
            mock_task.side_effect = mock_wfmanager_task_constructor

            mock_task = self.wfmanager_plugin_file._create_task()
            mock_task.open_workflow_file.assert_called()
