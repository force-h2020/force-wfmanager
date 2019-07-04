from traits.api import Instance, List, on_trait_change, Event, HasTraits

from traitsui.api import View, Item

from force_bdss.api import Workflow
from .notification_listener_model_view import NotificationListenerModelView


class CommunicationModelView(HasTraits):

    # -------------------
    # Required Attributes
    # -------------------

    model = Instance(Workflow)

    notification_listener_model_views = List(Instance(NotificationListenerModelView))

    # -------------------
    # Derived Attributes
    # -------------------

    verify_workflow_event = Event

    # -------------------
    #       View
    # -------------------

    traits_view = Instance(View)

    def default_traits_view(self):

        traits_view = View(
            Item('communication',
                 )
        )

        return traits_view

    @on_trait_change("model.notification_listeners[]")
    def update_notification_listeners_mv(self):
        """Updates the modelviews for the notification listeners, but ignoring
        any which are non UI visible"""
        self.notification_listener_model_views = [
            NotificationListenerModelView(
                model=notification_listener,
            )
            for notification_listener in self.model.notification_listeners
            if notification_listener.factory.ui_visible is True
        ]

    @on_trait_change('notification_listeners.verify_workflow_event')
    def received_verify_request(self):
        self.verify_workflow_event = True

    def add_notification_listener(self, notification_listener):
        """Adds a new notification listener"""
        self.model.notification_listeners.append(notification_listener)

    def remove_notification_listener(self, notification_listener):
        """Removes the notification listener from the model."""
        self.model.notification_listeners.remove(notification_listener)
