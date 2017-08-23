from force_bdss.api import BaseExtensionPlugin, plugin_id
from .ui_notification_factory import UINotificationFactory
from .ui_notification_hooks_factory import UINotificationHooksFactory


class UINotificationPlugin(BaseExtensionPlugin):
    id = plugin_id("enthought", "ui_notification")

    def _notification_listener_factories_default(self):
        return [UINotificationFactory(self)]

    def _ui_hooks_factories_default(self):
        return [UINotificationHooksFactory(self)]
