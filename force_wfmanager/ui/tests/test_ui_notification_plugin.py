import unittest

from force_wfmanager.ui.ui_notification_factory import \
    UINotificationFactory
from force_wfmanager.ui.ui_notification_hooks_factory \
    import \
    UINotificationHooksFactory
from force_wfmanager.ui.ui_notification_plugin import \
    UINotificationPlugin


class TestUINotificationPlugin(unittest.TestCase):
    def test_initialization(self):
        plugin = UINotificationPlugin()
        self.assertIsInstance(
            plugin.notification_listener_factories[0],
            UINotificationFactory)

        self.assertIsInstance(
            plugin.ui_hooks_factories[0],
            UINotificationHooksFactory)

        self.assertEqual(plugin.get_name(), "Workflow Manager support")
        self.assertEqual(plugin.get_description(),
                         "Plugin required to support the workflow "
                         "manager UI interface.")
        self.assertEqual(plugin.get_version(), 0)
