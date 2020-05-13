#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

from force_bdss.api import BaseExtensionPlugin, plugin_id

from .ui_notification_factory import UINotificationFactory
from .ui_notification_hooks_factory import UINotificationHooksFactory

PLUGIN_VERSION = 0


class UINotificationPlugin(BaseExtensionPlugin):
    id = plugin_id("enthought", "ui_notification", PLUGIN_VERSION)

    def get_name(self):
        return u"Workflow Manager support"

    def get_description(self):
        return u"Plugin required to support the workflow manager UI interface."

    def get_version(self):
        return PLUGIN_VERSION

    def get_factory_classes(self):
        return [
            UINotificationFactory,
            UINotificationHooksFactory,
        ]
