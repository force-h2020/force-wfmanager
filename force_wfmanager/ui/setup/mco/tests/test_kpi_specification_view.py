import unittest
from traits.testing.unittest_tools import UnittestTools
from force_bdss.api import OutputSlotInfo
from force_wfmanager.utils.tests.test_variable_names_registry import \
    get_basic_variable_names_registry

from force_bdss.api import KPISpecification
from force_wfmanager.ui.setup.mco.kpi_specification_view import \
    KPISpecificationView, KPISpecificationModelView


class TestKPISpecificationModelView(unittest.TestCase, UnittestTools):

    def setUp(self):

        self.kpi_model_view = KPISpecificationModelView(
            model=KPISpecification(name='T1'),
            _combobox_values=['T1', 'T2']
        )

    def test_kpi_model_view_init(self):
        self.assertEqual(
            "KPI: T1 (MINIMISE)",
            self.kpi_model_view.label
        )
        self.assertTrue(self.kpi_model_view.valid)

    def test_kpi_label(self):
        self.kpi_model_view.model.name = 'T2'
        self.assertEqual(
            "KPI: T2 (MINIMISE)",
            self.kpi_model_view.label
        )

    def test_verify_workflow_event(self):
        with self.assertTraitChanges(
                self.kpi_model_view, 'verify_workflow_event', count=1):
            self.kpi_model_view.model.name = 'T2'
        with self.assertTraitChanges(
                self.kpi_model_view, 'verify_workflow_event', count=2):
            self.kpi_model_view.model.name = 'not_in__combobox'

    def test__check_kpi_name(self):
        self.kpi_model_view._combobox_values.remove('T2')
        self.assertTrue(self.kpi_model_view.valid)
        self.kpi_model_view._combobox_values.remove('T1')
        self.assertEqual(
            "KPI",
            self.kpi_model_view.label
        )
        self.assertEqual('', self.kpi_model_view.model.name)
        error_message = self.kpi_model_view.model.verify()
        self.assertIn(
            'KPI is not named',
            error_message[0].local_error
        )


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
        self.assertEqual(
            self.kpi_view.selected_kpi,
            self.kpi_view.kpi_model_views[0]
        )

    def test_label(self):

        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]

        self.assertEqual(['T1'], self.registry.data_source_outputs)
        self.assertEqual(
            ['T1'], self.kpi_view.kpi_model_views[0]._combobox_values
        )
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
        self.assertEqual(1, len(self.kpi_view.kpi_name_options))

        self.kpi_view._add_kpi_button_fired()
        self.assertEqual(2, len(self.workflow.mco.kpis))
        self.assertEqual(2, len(self.kpi_view.kpi_model_views))

        kpi_model_view = self.kpi_view.kpi_model_views[1]
        kpi_model_view.model.name = 'T1'
        self.assertEqual('KPI: T1 (MINIMISE)', kpi_model_view.label)
        self.assertEqual(self.kpi_view.selected_kpi,
                         kpi_model_view)

    def test_remove_kpi(self):
        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        kpi_model_view = self.kpi_view.kpi_model_views[0]
        self.kpi_view.selected_kpi = kpi_model_view
        self.kpi_view._remove_kpi_button_fired()

        self.assertEqual(0, len(self.workflow.mco.kpis))
        self.assertEqual(0, len(self.kpi_view.kpi_model_views))
        self.assertIsNone(self.kpi_view.selected_kpi)

        self.kpi_view._add_kpi_button_fired()
        self.assertEqual(1, len(self.workflow.mco.kpis))
        self.assertEqual(self.kpi_view.kpi_model_views[0],
                         self.kpi_view.selected_kpi)

    def test_verify_workflow_event(self):
        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        kpi_model_view = self.kpi_view.kpi_model_views[0]
        with self.assertTraitChanges(
                self.kpi_view, 'verify_workflow_event', count=1):
            kpi_model_view.model.name = 'T1'
        with self.assertTraitChanges(
                self.kpi_view, 'verify_workflow_event', count=2):
            kpi_model_view.model.name = 'T2'

    def test__kpi_names_check(self):

        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        self.workflow.mco.kpis[0].name = 'T1'
        self.assertEqual('', self.kpi_view.error_message)

        self.data_source2.output_slot_info = [OutputSlotInfo(name='T2')]
        self.kpi_view._add_kpi_button_fired()
        self.workflow.mco.kpis[1].name = 'T2'
        self.assertEqual('', self.kpi_view.error_message)

        self.workflow.mco.kpis[0].name = 'T2'
        self.assertIn(
            'Two or more KPIs have a duplicate name',
            self.kpi_view.error_message,
        )
        self.assertFalse(self.kpi_view.valid)

    def test_variable_names_registry(self):

        self.kpi_view.variable_names_registry = None
        self.assertEqual(0, len(self.kpi_view.kpi_name_options))
        self.assertEqual(1, len(self.kpi_view.kpi_names))
        self.assertEqual(1, len(self.kpi_view.kpi_model_views))