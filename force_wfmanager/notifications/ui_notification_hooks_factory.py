from force_bdss.api import BaseUIHooksFactory
from .ui_notification_hooks_manager import UINotificationHooksManager


class UINotificationHooksFactory(BaseUIHooksFactory):
    def get_ui_hooks_manager_class(self):
        return UINotificationHooksManager

    def get_name(self):
        return "UI Notification Hooks"

    def get_identifier(self):
        return "ui_identification_hooks"
