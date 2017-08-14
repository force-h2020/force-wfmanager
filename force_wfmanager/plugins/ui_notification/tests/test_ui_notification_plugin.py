import unittest

from force_wfmanager.plugins.ui_notification.ui_notification_factory import \
    UINotificationFactory
from force_wfmanager.plugins.ui_notification.ui_notification_plugin import \
    UINotificationPlugin


class TestUINotificationPlugin(unittest.TestCase):
    def test_initialization(self):
        plugin = UINotificationPlugin()
        self.assertIsInstance(
            plugin.notification_listener_factories[0],
            UINotificationFactory)