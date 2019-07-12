import unittest
from traits.testing.unittest_tools import UnittestTools
from force_bdss.api import OutputSlotInfo
from force_wfmanager.utils.tests.test_variable_names_registry import \
    get_basic_variable_names_registry

from force_bdss.api import KPISpecification
from force_wfmanager.ui.setup.mco.kpi_specification_view import \
    KPISpecificationView, KPISpecificationModelView, TableRow


class TestKPISpecificationModelView(unittest.TestCase, UnittestTools):

    def setUp(self):

        self.kpi_model_view = KPISpecificationModelView(
            model=KPISpecification(name='kpi_test')
        )

    def test_kpi_model_view_init(self):
        self.assertEqual(
            "KPI: kpi_test (MINIMISE)",
            self.kpi_model_view.label
        )
        self.assertTrue(self.kpi_model_view.valid)

    def test_kpi_label(self):
        self.kpi_model_view.model.name = 'kpi_name_test'
        self.assertEqual(
            "KPI: kpi_name_test (MINIMISE)",
            self.kpi_model_view.label
        )

    def test_verify_workflow_event(self):
        with self.assertTraitChanges(
                self.kpi_model_view, 'verify_workflow_event', count=1):
            self.kpi_model_view.model.name = 'another'


class TestKPISpecificationView(unittest.TestCase, UnittestTools):

    def setUp(self):
        self.registry = get_basic_variable_names_registry()
        self.workflow = self.registry.workflow
        self.param1 = self.workflow.mco.parameters[0]
        self.param2 = self.workflow.mco.parameters[1]
        self.param3 = self.workflow.mco.parameters[2]
        self.data_source1 = self.workflow.execution_layers[0].data_sources[0]
        self.data_source2 = self.workflow.execution_layers[0].data_sources[1]
        self.workflow.mco.kpis.append(KPISpecification())

        self.kpi_view = KPISpecificationView(
            model=self.workflow.mco,
            variable_names_registry=self.registry
        )

    def test_kpi_view_init(self):
        self.assertEqual(1, len(self.kpi_view.kpi_names))
        self.assertEqual(1, len(self.kpi_view.kpi_model_views))
        self.assertEqual('KPI', self.kpi_view.kpi_model_views[0].label)
        self.assertEqual("MCO KPIs", self.kpi_view.label)

    def test_label(self):
        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]

        self.assertEqual(['T1'], self.registry.data_source_outputs)

        self.assertEqual('KPI', self.kpi_view.kpi_model_views[0].label)

        self.workflow.mco.kpis[0].name = 'T1'

        self.assertEqual(
            "KPI: T1 (MINIMISE)",
            self.kpi_view.kpi_model_views[0].label
        )

        self.workflow.mco.kpis[0].objective = 'MAXIMISE'

        self.assertEqual(
            "KPI: T1 (MAXIMISE)",
            self.kpi_view.kpi_model_views[0].label
        )

    def test_name_change(self):

        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        kpi_model_view = self.kpi_view.kpi_model_views[0]

        with self.assertTraitChanges(kpi_model_view, 'label', count=0):
            self.assertEqual('KPI', kpi_model_view.label)

        with self.assertTraitChanges(kpi_model_view, 'label', count=1):
            self.workflow.mco.kpis[0].name = 'T1'
            self.assertEqual('KPI: T1 (MINIMISE)', kpi_model_view.label)

    def test_add_kpi(self):

        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]

        self.kpi_view.selected_non_kpi = TableRow(
            name='T1', type='PRESSURE'
        )

        self.kpi_view._add_kpi_button_fired()

        self.assertEqual(2, len(self.workflow.mco.kpis))
        self.assertEqual(2, len(self.kpi_view.kpi_model_views))

        kpi_model_view = self.kpi_view.kpi_model_views[1]
        self.assertEqual('KPI: T1 (MINIMISE)', kpi_model_view.label)

    def test_remove_kpi(self):

        kpi_model_view = self.kpi_view.kpi_model_views[0]
        self.kpi_view.selected_kpi = kpi_model_view
        self.kpi_view._remove_kpi_button_fired()

        self.assertEqual(0, len(self.workflow.mco.kpis))
        self.assertEqual(0, len(self.kpi_view.kpi_model_views))

    def test_verify_workflow_event(self):
        kpi_model_view = self.kpi_view.kpi_model_views[0]

        with self.assertTraitChanges(
                self.kpi_view, 'verify_workflow_event', count=1):
            kpi_model_view.model.name = 'another'

    def test_no_variable_names_registry(self):

        self.kpi_view.variable_names_registry = None
        self.assertEqual(0, len(self.kpi_view.non_kpi_variables))
        self.assertIsNone(self.kpi_view.selected_non_kpi)

        self.kpi_view.add_kpi_button = True
        self.assertEqual(1, len(self.kpi_view.kpi_names))
        self.assertEqual(1, len(self.kpi_view.kpi_model_views))

    def test_no_kpi_selected(self):

        self.kpi_view.selected_kpi = None

        self.kpi_view.remove_kpi_button = True
        self.assertEqual(1, len(self.kpi_view.kpi_names))
        self.assertEqual(1, len(self.kpi_view.kpi_model_views))
