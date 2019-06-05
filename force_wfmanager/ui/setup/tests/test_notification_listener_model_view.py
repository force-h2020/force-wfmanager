import unittest

from force_bdss.tests.probe_classes.notification_listener import \
    ProbeNotificationListenerFactory
from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin
from force_wfmanager.ui.setup.notification_listener_model_view \
    import NotificationListenerModelView


class TestNotificationListenerModelView(unittest.TestCase):
    def setUp(self):
        self.plugin = ProbeExtensionPlugin()
        factory = ProbeNotificationListenerFactory(self.plugin)

        self.notification_listener_model = factory.create_model()
        self.notification_listener_mv = NotificationListenerModelView(
            model=self.notification_listener_model
        )

    def test_label(self):
        self.assertEqual(
            self.notification_listener_mv.label,
            "test_notification_listener")
