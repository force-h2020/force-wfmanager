import unittest

from force_bdss.tests.probe_classes.notification_listener import \
    ProbeNotificationListenerFactory
from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin
from force_wfmanager.ui.setup.communicator.\
    notification_listener_view \
    import NotificationListenerView


class TestNotificationListenerModelView(unittest.TestCase):

    def setUp(self):
        self.plugin = ProbeExtensionPlugin()
        factory = ProbeNotificationListenerFactory(self.plugin)

        self.notification_listener_model = factory.create_model()
        self.notification_listener_view = NotificationListenerView(
            model=self.notification_listener_model
        )

    def test_label(self):
        self.assertEqual(
            self.notification_listener_view.label,
            "test_notification_listener")
