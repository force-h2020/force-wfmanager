import unittest

from envisage.api import Plugin

from force_wfmanager.plugins.ui_notification.ui_notification_hooks_factory \
    import \
    UINotificationHooksFactory
from force_wfmanager.plugins.ui_notification.ui_notification_hooks_manager \
    import \
    UINotificationHooksManager

try:
    import mock
except ImportError:
    from unittest import mock


class TestUINotificationHooksFactory(unittest.TestCase):
    def test_initialization(self):
        mock_plugin = mock.Mock(spec=Plugin)
        factory = UINotificationHooksFactory(mock_plugin)
        self.assertEqual(factory.plugin, mock_plugin)

    def test_create_ui_hooks_manager(self):
        mock_plugin = mock.Mock(spec=Plugin)
        factory = UINotificationHooksFactory(mock_plugin)
        self.assertIsInstance(
            factory.create_ui_hooks_manager(),
            UINotificationHooksManager)
