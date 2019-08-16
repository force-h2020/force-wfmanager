from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin

from force_wfmanager.tests.dummy_classes.dummy_data_view import \
    DummyExtensionPluginWithDataView
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
