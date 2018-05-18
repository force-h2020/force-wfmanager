from force_bdss.api import BaseExtensionPlugin, plugin_id
from .ui_notification_factory import UINotificationFactory
from .ui_notification_hooks_factory import UINotificationHooksFactory


class UINotificationPlugin(BaseExtensionPlugin):
    id = plugin_id("enthought", "ui_notification", 0)

    def get_factory_classes(self):
        return [
            UINotificationFactory,
            UINotificationHooksFactory,
        ]
