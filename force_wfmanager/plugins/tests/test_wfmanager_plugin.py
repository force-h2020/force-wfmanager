import unittest
from unittest import mock

from envisage.api import Application

from force_wfmanager.plugins.wfmanager_plugin import WfManagerPlugin


SETUP_TASK = ("force_wfmanager.plugins.wfmanager_plugin"
              ".WfManagerSetupTask")
REVIEW_TASK = ("force_wfmanager.plugins.wfmanager_plugin"
               ".WfManagerReviewTask")
PLUGIN_SERVICE = 'envisage.api.Plugin.application.get_service'


def mock_wfmanager_task_constructor(*args, **kwargs):
    return


class TestWfManagerPlugin(unittest.TestCase):
    def setUp(self):
        self.wfmanager_plugin = WfManagerPlugin(workflow_file=None)
        self.wfmanager_plugin.application = mock.Mock(spec=Application)

    def test_init(self):
        self.assertEqual(len(self.wfmanager_plugin.tasks), 2)
        self.assertEqual(self.wfmanager_plugin.tasks[0].name,
                         "Workflow Manager (Setup)")
        self.assertEqual(self.wfmanager_plugin.tasks[1].name,
                         "Workflow Manager (Review)")

        with mock.patch(SETUP_TASK) as mock_setup_task:
            mock_setup_task.side_effect = mock_wfmanager_task_constructor

            self.wfmanager_plugin._create_setup_task()
            self.assertTrue(mock_setup_task.called)

        with mock.patch(REVIEW_TASK) as mock_review_task:
            mock_review_task.side_effect = mock_wfmanager_task_constructor

            self.wfmanager_plugin._create_review_task()
            self.assertTrue(mock_review_task.called)

    def test_init_with_file(self):
        self.wfmanager_plugin.workflow_file = 'some_workflow_file.json'

        with self.assertRaises(Exception):
            self.wfmanager_plugin.workflow_file = 0
