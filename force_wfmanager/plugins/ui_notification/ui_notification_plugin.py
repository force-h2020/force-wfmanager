from force_bdss.api import BaseExtensionPlugin
from .ui_notification_factory import UINotificationFactory
from .ui_notification_hooks_factory import UINotificationHooksFactory


class UINotificationPlugin(BaseExtensionPlugin):
    def get_producer(self):
        return "enthought"

    def get_identifier(self):
        return "ui_notification"

    def get_factory_classes(self):
        return [
            UINotificationFactory,
            UINotificationHooksFactory,
        ]
