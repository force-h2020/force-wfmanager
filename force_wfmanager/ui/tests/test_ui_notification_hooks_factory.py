import unittest

from force_wfmanager.ui.ui_notification_hooks_manager \
    import \
    UINotificationHooksManager
from force_wfmanager.ui.ui_notification_plugin import \
    UINotificationPlugin


class TestUINotificationHooksFactory(unittest.TestCase):
    def setUp(self):
        self.plugin = UINotificationPlugin()
        self.factory = self.plugin.ui_hooks_factories[0]

    def test_initialization(self):
        self.assertEqual(self.factory.plugin, self.plugin)

    def test_create_ui_hooks_manager(self):
        self.assertIsInstance(
            self.factory.create_ui_hooks_manager(),
            UINotificationHooksManager)
