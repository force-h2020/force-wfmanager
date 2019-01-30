from force_bdss.api import BaseUIHooksManager, factory_id

from .ui_notification_model import UINotificationModel


class UINotificationHooksManager(BaseUIHooksManager):
    """
    Modifies the model so that the notification for the UI is
    properly setup.
    When the execution ends, the added information is removed.
    """

    def before_execution(self, task):
        """ Sets up a
        :class:`UINotificationModel
        <.ui_notification_model.UINotificationModel>`
        instance and adds it to the workflow model.

        Parameters
        ----------
        task: pyface.tasks.task.Task
            The task containing the workflow model and the zmq server.

        Note
        ----
        The actual (:class:`UINotification <.ui_notification.UINotification>`)
        listener is set up when the bdss workflow is executed
        (see :mod:`force_bdss.core_mco_driver`)
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
        """Removes the :class:`UINotificationModel
        <.ui_notification_model.UINotificationModel>`
        instance from the workflow model, as
        the bdss has finished calculating.

        Parameters
        ----------
        task: pyface.tasks.task.Task
            The task containing the workflow model and the zmq server.
        """
        model = task.workflow_model
        notification_model = None
        for listener_model in model.notification_listeners:
            if isinstance(listener_model, UINotificationModel):
                notification_model = listener_model

        if notification_model is not None:
            model.notification_listeners.remove(notification_model)
