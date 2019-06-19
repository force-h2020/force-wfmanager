import unittest

from force_wfmanager.notifications.ui_notification import \
    UINotification
from force_wfmanager.notifications.ui_notification_model import \
    UINotificationModel
from force_wfmanager.notifications.ui_notification_plugin import \
    UINotificationPlugin


class TestUINotificationFactory(unittest.TestCase):
    def setUp(self):
        self.plugin = UINotificationPlugin()
        self.factory = self.plugin.notification_listener_factories[0]

    def test_initialization(self):
        self.assertEqual(
            self.factory.id,
            "force.bdss.enthought.plugin.ui_notification.v0."
            "factory.ui_notification")

    def test_create_model(self):
        model = self.factory.create_model()
        self.assertIsInstance(model, UINotificationModel)
        self.assertEqual(model.factory, self.factory)

        model = self.factory.create_model({})
        self.assertIsInstance(model, UINotificationModel)
        self.assertEqual(model.factory, self.factory)

    def test_create_listener(self):
        listener = self.factory.create_listener()
        self.assertIsInstance(listener, UINotification)
