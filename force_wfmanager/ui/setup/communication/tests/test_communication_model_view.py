import unittest

from force_bdss.api import Workflow
from force_bdss.tests.probe_classes.notification_listener import \
    ProbeNotificationListenerFactory
from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin
from force_wfmanager.ui.setup.communication.\
    communication_model_view import \
    CommunicationModelView


class TestCommunicationModelView(unittest.TestCase):

    def setUp(self):
        self.communication_model_view = CommunicationModelView(
            model=Workflow()
        )
        self.plugin = ProbeExtensionPlugin()
        self.factory = ProbeNotificationListenerFactory(self.plugin)

    def test_add_notification_listener(self):
        self.assertEqual(len(self.communication_model_view.notification_listener_model_views), 0)
        self.communication_model_view.add_notification_listener(
            self.factory.create_model())
        self.assertEqual(len(self.communication_model_view.notification_listener_model_views), 1)

    def test_remove_notification_listener(self):
        model = self.factory.create_model()
        self.communication_model_view.add_notification_listener(model)
        self.assertEqual(len(self.communication_model_view.notification_listener_model_views), 1)
        self.communication_model_view.remove_notification_listener(model)
        self.assertEqual(len(self.communication_model_view.notification_listener_model_views), 0)
