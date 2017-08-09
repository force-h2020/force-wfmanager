import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from envisage.api import Application

from force_wfmanager.wfmanager_plugin import WfManagerPlugin

WFMANAGER_TASK_PATH = "force_wfmanager.wfmanager_plugin.WfManagerTask"


class WfManagerPluginTest(unittest.TestCase):
    def setUp(self):
        self.wfmanager_plugin = WfManagerPlugin()
        self.wfmanager_plugin.application = mock.Mock(spec=Application)

    def test_init(self):
        self.assertEqual(len(self.wfmanager_plugin.tasks), 1)
        self.assertEqual(self.wfmanager_plugin.tasks[0].name,
                         "Workflow Manager")

        def mock_wfmanager_task_constructor(*args, **kwargs):
            return

        with mock.patch(WFMANAGER_TASK_PATH) as mock_task:
            mock_task.side_effect = mock_wfmanager_task_constructor

            self.wfmanager_plugin._create_task()
            mock_task.assert_called()
