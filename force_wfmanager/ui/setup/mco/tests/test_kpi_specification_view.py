import unittest
from traits.testing.unittest_tools import UnittestTools
from traits.trait_errors import TraitError
from force_bdss.api import OutputSlotInfo
from force_wfmanager.utils.tests.test_variable_names_registry import \
    get_basic_variable_names_registry

from force_bdss.api import KPISpecification
from force_wfmanager.ui.setup.mco.kpi_specification_view import \
    KPISpecificationView


class TestKPISpecificationView(unittest.TestCase, UnittestTools):

    def setUp(self):
        self.registry = get_basic_variable_names_registry()
        self.workflow = self.registry.workflow
        self.param1 = self.workflow.mco.parameters[0]
        self.param2 = self.workflow.mco.parameters[1]
        self.param3 = self.workflow.mco.parameters[2]
        self.data_source1 = self.workflow.execution_layers[0].data_sources[0]
        self.data_source2 = self.workflow.execution_layers[0].data_sources[1]

        self.kpi_view = KPISpecificationView(
            model=KPISpecification(),
            variable_names_registry=self.registry
        )

    def test_kpi_view_init(self):
        with self.assertRaises(TypeError):
            KPISpecificationView(
                variable_names_registry=self.registry
            )
        self.assertEqual(self.kpi_view.label, "KPI")

    def test_update_combobox_values(self):
        self.assertEqual(self.kpi_view._combobox_values, [''])

        self.param1.name = 'V1'
        self.param2.name = 'V2'
        self.param3.name = 'V3'

        self.assertEqual(self.kpi_view._combobox_values, [''])

        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        self.data_source2.output_slot_info = [OutputSlotInfo(name='T2')]

        self.assertEqual(self.kpi_view._combobox_values,
                         ['', 'T1', 'T2'])

    def test_label(self):
        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]

        self.assertEqual(self.kpi_view.label, "KPI")
        self.kpi_view_named = KPISpecificationView(
            model=KPISpecification(name='T1'),
            variable_names_registry=self.registry
        )
        self.assertEqual(self.kpi_view_named.label,
                         "KPI: T1 (MINIMISE)")

        self.kpi_specification_objective = KPISpecification(
            name='T1', objective='MAXIMISE')
        self.kpi_view_objective = KPISpecificationView(
            model=self.kpi_specification_objective,
            variable_names_registry=self.registry)
        self.assertEqual(self.kpi_view_objective.label,
                         "KPI: T1 (MAXIMISE)")

    def test_name_change(self):
        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        with self.assertTraitChanges(self.kpi_view, 'label',
                                     count=0):
            self.assertEqual(self.kpi_view.label, 'KPI')
        with self.assertTraitChanges(self.kpi_view, 'label',
                                     count=1):
            self.kpi_view.model.name = 'T1'
            self.assertEqual(self.kpi_view.label,
                             'KPI: T1 (MINIMISE)')
        self.kpi_view_nomodel = KPISpecificationView(
            model=None, variable_names_registry=self.registry)
        self.assertEqual(self.kpi_view_nomodel.name, '')
