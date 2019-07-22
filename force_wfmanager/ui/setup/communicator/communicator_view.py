from traits.api import (
    Instance, List, on_trait_change, Event, HasTraits
)
from traitsui.api import View, Item

from force_bdss.api import Workflow
from .notification_listener_view import NotificationListenerView


class CommunicatorView(HasTraits):
    """This class is a container for a list of NotificationListenerViews
    corresponding to each NotificationListenerin the Workflow.
    It has the same the hierarchy as MCOView and ProcessView classes"""

    # -------------------
    # Required Attributes
    # -------------------

    #: Workflow model object containing notification listeners
    model = Instance(Workflow)

    #: List of views for model.notification_listeners
    notification_listener_views = List(Instance(NotificationListenerView))

    # -------------------
    # Derived Attributes
    # -------------------

    verify_workflow_event = Event

    # -------------------
    #       View
    # -------------------

    def default_traits_view(self):

        traits_view = View(
            Item('notification_listener_views',
                 )
        )

        return traits_view

    # -------------------
    #      Listeners
    # -------------------

    @on_trait_change("model.notification_listeners[]")
    def update_notification_listener_views(self):
        """Updates the views for the notification listeners, but ignores
        any which are non UI visible"""
        self.notification_listener_views = [
            NotificationListenerView(
                model=notification_listener,
            )
            for notification_listener in self.model.notification_listeners
            if notification_listener.factory.ui_visible is True
        ]

    @on_trait_change('notification_listeners.verify_workflow_event')
    def received_verify_request(self):
        self.verify_workflow_event = True

    # -------------------
    #    Public Methods
    # -------------------

    def add_notification_listener(self, notification_listener):
        """Adds a new notification listener"""
        self.model.notification_listeners.append(notification_listener)

    def remove_notification_listener(self, notification_listener):
        """Removes the notification listener from the model."""
        self.model.notification_listeners.remove(notification_listener)
