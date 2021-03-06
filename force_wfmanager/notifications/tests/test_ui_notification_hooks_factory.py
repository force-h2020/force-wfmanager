#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

import unittest

from force_wfmanager.notifications.ui_notification_hooks_manager \
    import \
    UINotificationHooksManager
from force_wfmanager.notifications.ui_notification_plugin import \
    UINotificationPlugin


class TestUINotificationHooksFactory(unittest.TestCase):
    def setUp(self):
        self.plugin = UINotificationPlugin()
        self.factory = self.plugin.ui_hooks_factories[0]

    def test_initialization(self):
        self.assertEqual(self.factory.plugin_id, self.plugin.id)
        self.assertEqual(self.factory.plugin_name, self.plugin.name)

    def test_create_ui_hooks_manager(self):
        self.assertIsInstance(
            self.factory.create_ui_hooks_manager(),
            UINotificationHooksManager)
