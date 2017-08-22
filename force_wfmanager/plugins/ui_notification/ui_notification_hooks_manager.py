from force_bdss.api import BaseUIHooksManager, factory_id

from .ui_notification_model import UINotificationModel


class UINotificationHooksManager(BaseUIHooksManager):
    def before_execution(self, task):
        model = task.workflow_m
        notification_model = None
        for listener_model in model.notification_listeners:
            if isinstance(listener_model, UINotificationModel):
                notification_model = listener_model

        if notification_model is None:
            registry = task.factory_registry
            nl_factory = registry.notification_listener_factory_by_id(
                factory_id("enthought", "ui_notification")
            )
            notification_model = nl_factory.create_model()
            model.notification_listeners.append(notification_model)

        notification_model.sync_url = "tcp://127.0.0.1:"+_zmq_port(
            task.zmq_server_config.sync_url)
        notification_model.pub_url = "tcp://127.0.0.1:"+_zmq_port(
            task.zmq_server_config.pub_url)
        notification_model.identifier = ""

    def before_save(self, task):
        model = task.workflow_m
        notification_model = None
        for listener_model in model.notification_listeners:
            if isinstance(listener_model, UINotificationModel):
                notification_model = listener_model

        if notification_model is not None:
            model.notification_listeners.remove(notification_model)


def _zmq_port(zmq_url):
    return zmq_url.split(":")[-1]
