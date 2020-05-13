#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin

from force_wfmanager.tests.dummy_classes.dummy_data_view import (
    DummyExtensionPluginWithDataView
)
from force_wfmanager.tests.dummy_classes.dummy_contributed_ui import (
    DummyUIPlugin, DummyUIPluginOld
)
from force_wfmanager.wfmanager import WfManager


class DummyWfManager(WfManager):

    def __init__(self):

        plugins = [CorePlugin(), TasksPlugin()]
        super(DummyWfManager, self).__init__(plugins=plugins)

    def run(self):
        pass


class DummyWfManagerWithPlugins(WfManager):

    def __init__(self):
        plugins = [
            CorePlugin(),
            TasksPlugin(),
            DummyExtensionPluginWithDataView()
        ]
        super(DummyWfManagerWithPlugins, self).__init__(plugins=plugins)

    def run(self):
        pass


class DummyUIWfManager(WfManager):
    """A workflow manager with a plugin contributing a UI"""
    def __init__(self):
        plugins = [
            CorePlugin(), TasksPlugin(), DummyUIPlugin(), DummyUIPluginOld()
        ]
        super(DummyUIWfManager, self).__init__(plugins=plugins)

    def run(self):
        pass
