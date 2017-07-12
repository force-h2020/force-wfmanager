from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin

from force_wfmanager.wfmanager import WfManager
from force_wfmanager.wfmanager_plugin import WfManagerPlugin


def main():
    plugins = [CorePlugin(), TasksPlugin(), WfManagerPlugin()]
    wfmanager = WfManager(plugins=plugins)
    wfmanager.run()
