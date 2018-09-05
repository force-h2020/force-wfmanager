from force_bdss.api import BaseUIHooksManager, factory_id
from force_wfmanager.api import UINotificationModel


class UINotificationHooksManager(BaseUIHooksManager):
    """
    Modifies the model so that the notification for the UI is
    properly setup.
    When the execution ends, the added information is removed.
    """

    def before_execution(self, task):
        """Sets up the ui_notification notification listener, which
        listens to the ports for the ZMQ server for incoming data
        from the bdss.

        Parameters
        ----------
        task:
            The WfManagerResultsTask instance containing the workflow
            model and the zmq server.
        """
        model = task.workflow_model
        notification_model = None
        for listener_model in model.notification_listeners:
            if isinstance(listener_model, UINotificationModel):
                notification_model = listener_model

        if notification_model is None:
            registry = task.factory_registry
            nl_factory = registry.notification_listener_factory_by_id(
                factory_id(self.factory.plugin.id, "ui_notification")
            )
            notification_model = nl_factory.create_model()
            model.notification_listeners.append(notification_model)

        pub_port, sync_port = task.zmq_server.ports
        notification_model.sync_url = (
                "tcp://127.0.0.1:"+str(sync_port))
        notification_model.pub_url = (
                "tcp://127.0.0.1:"+str(pub_port))
        notification_model.identifier = ""

    def after_execution(self, task):
        """Removes the ui_notification notification listener, as
        the bdss has finished calculating.

        Parameters
        ----------
        task:
            The WfManagerResultsTask instance instance containing the workflow
            model and the zmq server.
        """
        model = task.workflow_model
        notification_model = None
        for listener_model in model.notification_listeners:
            if isinstance(listener_model, UINotificationModel):
                notification_model = listener_model

        if notification_model is not None:
            model.notification_listeners.remove(notification_model)
