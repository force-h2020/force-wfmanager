from traits.api import Bool

from force_bdss.api import BaseNotificationListenerFactory

from .ui_notification import UINotification
from .ui_notification_model import UINotificationModel


class UINotificationFactory(BaseNotificationListenerFactory):
    ui_visible = Bool(False)

    def get_model_class(self):
        return UINotificationModel

    def get_listener_class(self):
        return UINotification

    def get_name(self):
        return "UI Notification"

    def get_identifier(self):
        return "ui_notification"
