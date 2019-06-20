import unittest
from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import OutputSlotInfo
from force_wfmanager.utils.tests.test_variable_names_registry import \
    get_basic_variable_names_registry

from force_bdss.api import KPISpecification
from force_wfmanager.ui.setup.mco.kpi_specification_model_view import \
    KPISpecificationModelView


class TestKPISpecificationModelViewTest(unittest.TestCase, UnittestTools):
    def setUp(self):
        self.registry = get_basic_variable_names_registry()
        self.workflow = self.registry.workflow
        self.param1 = self.workflow.mco.parameters[0]
        self.param2 = self.workflow.mco.parameters[1]
        self.param3 = self.workflow.mco.parameters[2]
        self.data_source1 = self.workflow.execution_layers[0].data_sources[0]
        self.data_source2 = self.workflow.execution_layers[0].data_sources[1]

        self.kpi_specification_mv = KPISpecificationModelView(
            model=KPISpecification(),
            variable_names_registry=self.registry
        )

    def test_kpi_specification_mv_init(self):
        self.assertEqual(self.kpi_specification_mv.label, "KPI")

    def test_update_combobox_values(self):
        self.assertEqual(self.kpi_specification_mv._combobox_values, [''])

        self.param1.name = 'V1'
        self.param2.name = 'V2'
        self.param3.name = 'V3'

        self.assertEqual(self.kpi_specification_mv._combobox_values, [''])

        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        self.data_source2.output_slot_info = [OutputSlotInfo(name='T2')]

        self.assertEqual(self.kpi_specification_mv._combobox_values,
                         ['', 'T1', 'T2'])

    def test_label(self):
        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]

        self.assertEqual(self.kpi_specification_mv.label, "KPI")
        self.kpi_specification_mv_named = KPISpecificationModelView(
            model=KPISpecification(name='T1'),
            variable_names_registry=self.registry
        )
        self.assertEqual(self.kpi_specification_mv_named.label,
                         "KPI: T1 (MINIMISE)")

        self.kpi_specification_objective = KPISpecification(
            name='T1', objective='MAXIMISE')
        self.kpi_specification_mv_objective = KPISpecificationModelView(
            model=self.kpi_specification_objective,
            variable_names_registry=self.registry)
        self.assertEqual(self.kpi_specification_mv_objective.label,
                         "KPI: T1 (MAXIMISE)")

    def test_name_change(self):
        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        with self.assertTraitChanges(self.kpi_specification_mv, 'label',
                                     count=0):
            self.assertEqual(self.kpi_specification_mv.label, 'KPI')
        with self.assertTraitChanges(self.kpi_specification_mv, 'label',
                                     count=1):
            self.kpi_specification_mv.model.name = 'T1'
            self.assertEqual(self.kpi_specification_mv.label,
                             'KPI: T1 (MINIMISE)')
        self.kpi_specification_mv_nomodel = KPISpecificationModelView(
            model=None, variable_names_registry=self.registry)
        self.assertEqual(self.kpi_specification_mv_nomodel.name, '')