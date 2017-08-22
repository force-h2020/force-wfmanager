import unittest

from pyface.tasks.task import Task

from force_bdss.core.workflow import Workflow
from force_bdss.factory_registry_plugin import FactoryRegistryPlugin
from force_wfmanager.plugins.ui_notification.ui_notification_factory import \
    UINotificationFactory
from force_wfmanager.plugins.ui_notification.ui_notification_hooks_factory \
    import \
    UINotificationHooksFactory
from force_wfmanager.plugins.ui_notification.ui_notification_hooks_manager \
    import \
    UINotificationHooksManager
from force_wfmanager.plugins.ui_notification.ui_notification_model import \
    UINotificationModel
from force_wfmanager.plugins.ui_notification.ui_notification_plugin import \
    UINotificationPlugin
from force_wfmanager.server.zmq_server_config import ZMQServerConfig

try:
    import mock
except ImportError:
    from unittest import mock


class TestUINotificationHooksManager(unittest.TestCase):
    def test_initialization(self):
        mock_factory = mock.Mock(spec=UINotificationHooksFactory)
        manager = UINotificationHooksManager(factory=mock_factory)
        self.assertEqual(manager.factory, mock_factory)

    def test_before_and_after_execution(self):
        mock_factory = mock.Mock(spec=UINotificationHooksFactory)
        manager = UINotificationHooksManager(factory=mock_factory)

        mock_task = mock.Mock(spec=Task)
        mock_task.zmq_server_config = ZMQServerConfig()
        mock_registry = mock.Mock(spec=FactoryRegistryPlugin)
        mock_task.factory_registry = mock_registry
        mock_registry.notification_listener_factory_by_id.return_value \
            = UINotificationFactory(mock.Mock(spec=UINotificationPlugin))

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

        self.assertEqual(model.sync_url, "tcp://127.0.0.1:54538")
        self.assertEqual(model.pub_url, "tcp://127.0.0.1:54537")

        manager.after_execution(mock_task)

        self.assertNotIn(model, workflow.notification_listeners)

        manager.after_execution(mock_task)
        self.assertNotIn(model, workflow.notification_listeners)

