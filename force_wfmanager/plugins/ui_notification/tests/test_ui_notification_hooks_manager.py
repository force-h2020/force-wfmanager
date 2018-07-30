import unittest

from pyface.tasks.task import Task

from force_bdss.api import FactoryRegistryPlugin, Workflow
from force_wfmanager.plugins.ui_notification.ui_notification_model import \
    UINotificationModel
from force_wfmanager.plugins.ui_notification.ui_notification_plugin import \
    UINotificationPlugin
from force_wfmanager.server.zmq_server import ZMQServer

from unittest import mock


class TestUINotificationHooksManager(unittest.TestCase):
    def setUp(self):
        self.plugin = UINotificationPlugin()
        self.factory = self.plugin.ui_hooks_factories[0]
        self.nl_factory = self.plugin.notification_listener_factories[0]

    def test_initialization(self):
        manager = self.factory.create_ui_hooks_manager()
        self.assertEqual(manager.factory, self.factory)

    def test_before_and_after_execution(self):
        manager = self.factory.create_ui_hooks_manager()

        mock_task = mock.Mock(spec=Task)
        mock_registry = mock.Mock(spec=FactoryRegistryPlugin)
        mock_task.factory_registry = mock_registry
        mock_server = mock.Mock(spec=ZMQServer)
        mock_server.ports = (54537, 54538)
        mock_task.zmq_server = mock_server
        mock_registry.notification_listener_factory_by_id.return_value \
            = self.nl_factory

        workflow = Workflow()
        mock_task.workflow_m = workflow
        manager.before_execution(mock_task)

        model = workflow.notification_listeners[0]
        self.assertIsInstance(model, UINotificationModel)

        # Repeat the operation to check if no new model is created.
        manager.before_execution(mock_task)

        self.assertEqual(len(workflow.notification_listeners), 1)
        self.assertEqual(model, workflow.notification_listeners[0])
        self.assertIsInstance(model, UINotificationModel)

        self.assertEqual(model.pub_url, "tcp://127.0.0.1:54537")
        self.assertEqual(model.sync_url, "tcp://127.0.0.1:54538")

        manager.after_execution(mock_task)

        self.assertNotIn(model, workflow.notification_listeners)

        manager.after_execution(mock_task)
        self.assertNotIn(model, workflow.notification_listeners)
