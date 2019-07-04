import unittest

from force_bdss.api import Workflow
from force_bdss.tests.probe_classes.notification_listener import \
    ProbeNotificationListenerFactory
from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin
from force_wfmanager.ui.setup.communication.\
    communication_view import \
    CommunicationView


class TestCommunicationView(unittest.TestCase):

    def setUp(self):
        self.communication_view = CommunicationView(
            model=Workflow()
        )
        self.plugin = ProbeExtensionPlugin()
        self.factory = ProbeNotificationListenerFactory(self.plugin)

    def test_add_notification_listener(self):
        self.assertEqual(len(self.communication_view.notification_listener_views), 0)
        self.communication_view.add_notification_listener(
            self.factory.create_model())
        self.assertEqual(len(self.communication_view.notification_listener_views), 1)

    def test_remove_notification_listener(self):
        model = self.factory.create_model()
        self.communication_view.add_notification_listener(model)
        self.assertEqual(len(self.communication_view.notification_listener_views), 1)
        self.communication_view.remove_notification_listener(model)
        self.assertEqual(len(self.communication_view.notification_listener_views), 0)
