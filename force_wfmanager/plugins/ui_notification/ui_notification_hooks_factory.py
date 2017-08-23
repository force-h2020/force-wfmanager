from force_bdss.api import BaseUIHooksFactory, factory_id
from .ui_notification_hooks_manager import UINotificationHooksManager


class UINotificationHooksFactory(BaseUIHooksFactory):
    id = factory_id("enthought", "ui_notification_hooks")

    def create_ui_hooks_manager(self):
        return UINotificationHooksManager(self)
