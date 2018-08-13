from force_bdss.api import BaseUIHooksManager, factory_id

from .ui_notification_model import UINotificationModel


class UINotificationHooksManager(BaseUIHooksManager):
    """
    Modifies the model so that the notification for the UI is
    properly setup.
    When the execution ends, the added information is removed.
    """
    def before_execution(self, task):
        model = task.app.workflow_m
        notification_model = None
        for listener_model in model.notification_listeners:
            if isinstance(listener_model, UINotificationModel):
                notification_model = listener_model

        if notification_model is None:
            registry = task.app.factory_registry
            nl_factory = registry.notification_listener_factory_by_id(
                factory_id(self.factory.plugin.id, "ui_notification")
            )
            notification_model = nl_factory.create_model()
            model.notification_listeners.append(notification_model)

        pub_port, sync_port = task.app.zmq_server.ports
        notification_model.sync_url = (
                "tcp://127.0.0.1:"+str(sync_port))
        notification_model.pub_url = (
                "tcp://127.0.0.1:"+str(pub_port))
        notification_model.identifier = ""

    def after_execution(self, task):
        model = task.app.workflow_m
        notification_model = None
        for listener_model in model.notification_listeners:
            if isinstance(listener_model, UINotificationModel):
                notification_model = listener_model

        if notification_model is not None:
            model.notification_listeners.remove(notification_model)
