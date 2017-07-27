from envisage.api import Plugin, ExtensionPoint
from envisage.ui.tasks.api import TaskFactory
from traits.api import List, Instance

from force_bdss.ids import ExtensionPointID


class WfManagerPlugin(Plugin):
    """ The basic WfManager """

    TASKS = 'envisage.ui.tasks.tasks'

    id = 'force_wfmanager.wfmanager_plugin'
    name = 'Workflow Manager'

    tasks = List(contributes_to=TASKS)

    mco_bundles = ExtensionPoint(
        List(Instance('force_bdss.mco.i_mco_bundle.IMCOBundle')),
        id=ExtensionPointID.MCO_BUNDLES,
        desc="""
        Available MCOs for the Workflow Manager
        """
    )

    data_source_bundles = ExtensionPoint(
        List(Instance('force_bdss.data_sources.i_data_source_bundle.'
                      'IDataSourceBundle')),
        id=ExtensionPointID.DATA_SOURCE_BUNDLES,
        desc="""
        Available Datasources for the Workflow Manager
        """
    )

    kpi_calculator_bundles = ExtensionPoint(
        List(Instance('force_bdss.kpi.i_kpi_calculator_bundle.'
                      'IKPICalculatorBundle')),
        id=ExtensionPointID.KPI_CALCULATOR_BUNDLES,
        desc="""
        Available KPI calculators for the Workflow Manager
        """
    )

    def _tasks_default(self):
        return [TaskFactory(id='force_wfmanager.wfmanager_task',
                            name='Workflow Manager',
                            factory=self._create_task)]

    def _create_task(self):
        from force_wfmanager.wfmanager_task import WfManagerTask

        return WfManagerTask(
            mco_bundles=self.mco_bundles,
            data_source_bundles=self.data_source_bundles,
            kpi_calculator_bundles=self.kpi_calculator_bundles)
