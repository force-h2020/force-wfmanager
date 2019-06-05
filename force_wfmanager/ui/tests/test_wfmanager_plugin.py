import unittest
from unittest import mock

from envisage.api import Application

from force_wfmanager.ui.wfmanager_plugin import WfManagerPlugin


class TestWfManagerPlugin(unittest.TestCase):
    def setUp(self):
        self.wfmanager_plugin = WfManagerPlugin(workflow_file=None)
        self.wfmanager_plugin.application = mock.Mock(spec=Application)

    def test_init(self):
        self.assertEqual(len(self.wfmanager_plugin.tasks), 2)
        self.assertEqual(self.wfmanager_plugin.tasks[0].name,
                         "Workflow Manager (Setup)")
        self.assertEqual(self.wfmanager_plugin.tasks[1].name,
                         "Workflow Manager (Results)")

        def mock_wfmanager_task_constructor(*args, **kwargs):
            return

        with mock.patch(
                "force_wfmanager.ui.wfmanager_plugin"
                ".WfManagerSetupTask") as mock_setup_task:
            mock_setup_task.side_effect = mock_wfmanager_task_constructor

            self.wfmanager_plugin._create_setup_task()
            self.assertTrue(mock_setup_task.called)

        with mock.patch(
                "force_wfmanager.ui.wfmanager_plugin"
                ".WfManagerResultsTask") as mock_results_task:
            mock_results_task.side_effect = mock_wfmanager_task_constructor

            self.wfmanager_plugin._create_results_task()
            self.assertTrue(mock_results_task.called)

    def test_init_with_file(self):
        pass
