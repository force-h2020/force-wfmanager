from envisage.core_plugin import CorePlugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin

from force_bdss.kpi.key_performance_calculators_plugin import (
    KeyPerformanceCalculatorsPlugin)
from force_bdss.mco.multi_criteria_optimizers_plugin import (
    MultiCriteriaOptimizersPlugin)

from force_wfmanager.wfmanager import WfManager
from force_wfmanager.wfmanager_plugin import WfManagerPlugin


def main():
    plugins = [CorePlugin(), TasksPlugin(), WfManagerPlugin(),
               KeyPerformanceCalculatorsPlugin(),
               MultiCriteriaOptimizersPlugin()]
    wfmanager = WfManager(plugins=plugins)
    wfmanager.run()
