from traits.api import Instance, List, on_trait_change, Event, HasTraits

from traitsui.api import View, Item

from force_bdss.api import Workflow
from .notification_listener_model_view import NotificationListenerModelView


class NotificationListenerInfo(HasTraits):

    workflow_model = Instance(Workflow)

    notification_listeners = List(Instance(NotificationListenerModelView))

    verify_workflow_event = Event

    traits_view = Instance(View)

    def default_traits_view(self):

        traits_view = View(
            Item('notification_listeners',
                 )
        )

        return traits_view

    @on_trait_change("workflow_model.notification_listeners[]")
    def update_notification_listeners_mv(self):
        """Updates the modelviews for the notification listeners, but ignoring
        any which are non UI visible"""
        self.notification_listeners_mv = [
            NotificationListenerModelView(
                model=notification_listener,
            )
            for notification_listener in self.workflow_model.notification_listeners
            if notification_listener.factory.ui_visible is True
        ]

    @on_trait_change('notification_listeners.verify_workflow_event')
    def received_verify_request(self):
        self.verify_workflow_event = True
