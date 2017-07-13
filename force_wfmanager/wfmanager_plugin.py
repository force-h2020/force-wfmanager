from envisage.api import Plugin, ExtensionPoint
from envisage.ui.tasks.api import TaskFactory
from traits.api import List, Instance


class WfManagerPlugin(Plugin):
    """ The basic WfManager """

    TASKS = 'envisage.ui.tasks.tasks'

    MCOS = 'force_bdss.multi_criteria_optimizers'
    KPIS = 'force_bdss.key_performance_calculators'

    id = 'force_wfmanager.wfmanager_plugin'
    name = 'Workflow Manager'

    tasks = List(contributes_to=TASKS)

    mcos = ExtensionPoint(
        List(Instance('force_bdss.mco.i_multi_criteria_optimizers.' +
                      'IMultiCriteriaOptimizer')),
        id=MCOS,
        desc="""
        Available MCOs for the Workflow Manager
        """
    )

    kpis = ExtensionPoint(
        List(Instance('force_bdss.kpi.i_key_performance_calculator.' +
                      'IKeyPerformanceCalculator')),
        id=KPIS,
        desc="""
        Available KPIs for the Workflow Manager
        """
    )

    def _tasks_default(self):
        return [TaskFactory(id='force_wfmanager.wfmanager_task',
                            name='Workflow Manager',
                            factory=self._create_task)]

    def _create_task(self):
        from force_wfmanager.wfmanager_task import WfManagerTask

        return WfManagerTask(mcos=self.mcos, kpis=self.kpis)
