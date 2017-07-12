from envisage.api import Plugin, ExtensionPoint
from envisage.ui.tasks.api import TaskFactory
from traits.api import List, Instance


class WfManagerPlugin(Plugin):
    """ The basic WfManager """

    TASKS = 'envisage.ui.tasks.tasks'

    MCOS = 'force_wfmanager.mcos'
    KPIS = 'force_wfmanager.kpis'
    CONSTRAINTS = 'force_wfmanager.constraints'

    id = 'force_wfmanager.wfmanager_plugin'
    name = 'Workflow Manager'

    tasks = List(contributes_to=TASKS)

    mcos = ExtensionPoint(
        List(Instance('force_wfmanager.spec.mco.IMCO')),
        id=MCOS,
        desc="""
        Available MCOs for the Workflow Manager
        """
    )

    kpis = ExtensionPoint(
        List(Instance('force_wfmanager.spec.kpi.IKPI')),
        id=KPIS,
        desc="""
        Available KPIs for the Workflow Manager
        """
    )

    constraints = ExtensionPoint(
        List(Instance('force_wfmanager.spec.constraint.IConstraint')),
        id=KPIS,
        desc="""
        Defined constraints for the Workflow Manager
        """
    )

    def _tasks_default(self):
        from force_wfmanager.wfmanager_task import WfManagerTask

        return [TaskFactory(id='force_wfmanager.wfmanager_task',
                            name='Workflow Manager',
                            factory=WfManagerTask)]
