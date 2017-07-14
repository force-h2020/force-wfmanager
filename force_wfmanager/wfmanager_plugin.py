from envisage.api import Plugin, ExtensionPoint
from envisage.ui.tasks.api import TaskFactory
from traits.api import List, Instance


class WfManagerPlugin(Plugin):
    """ The basic WfManager """

    TASKS = 'envisage.ui.tasks.tasks'

    MCOS_BUNDLES = 'force.bdss.mco.bundles'
    DATA_SOURCES_BUNDLES = 'force.bdss.data_sources.bundles'

    id = 'force_wfmanager.wfmanager_plugin'
    name = 'Workflow Manager'

    tasks = List(contributes_to=TASKS)

    mco_bundles = ExtensionPoint(
        List(Instance('force_bdss.mco.i_multi_criteria_optimizer_bundle.'
                      'IMultiCriteriaOptimizerBundle')),
        id=MCOS_BUNDLES,
        desc="""
        Available MCOs for the Workflow Manager
        """
    )

    data_source_bundles = ExtensionPoint(
        List(Instance('force_bdss.data_sources.i_data_source_bundle.'
                      'IDataSourceBundle')),
        id=DATA_SOURCES_BUNDLES,
        desc="""
        Available Datasources for the Workflow Manager
        """
    )

    def _tasks_default(self):
        return [TaskFactory(id='force_wfmanager.wfmanager_task',
                            name='Workflow Manager',
                            factory=self._create_task)]

    def _create_task(self):
        from force_wfmanager.wfmanager_task import WfManagerTask

        return WfManagerTask(mco_bundles=self.mco_bundles,
                             data_source_bundles=self.data_source_bundles)
