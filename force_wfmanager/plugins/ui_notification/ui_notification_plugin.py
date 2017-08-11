from force_bdss.api import BaseExtensionPlugin, plugin_id
from .ui_notification_factory import UINotificationFactory


class UINotificationPlugin(BaseExtensionPlugin):
    id = plugin_id("enthought", "ui_notification")

    def _notification_listener_factories_default(self):
        return [UINotificationFactory(self)]
