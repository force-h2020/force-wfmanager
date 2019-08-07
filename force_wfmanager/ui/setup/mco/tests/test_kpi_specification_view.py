import unittest

from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import KPISpecification

from force_wfmanager.ui.setup.mco.kpi_specification_view import \
    KPISpecificationView
from force_wfmanager.utils.tests.test_variable_names_registry import \
    get_basic_workflow
from force_wfmanager.utils.variable import Variable


class TestKPISpecificationView(unittest.TestCase, UnittestTools):

    def setUp(self):
        self.workflow = get_basic_workflow()
        self.param1 = self.workflow.mco.parameters[0]
        self.param2 = self.workflow.mco.parameters[1]
        self.param3 = self.workflow.mco.parameters[2]
        self.data_source1 = self.workflow.execution_layers[0].data_sources[0]
        self.data_source2 = self.workflow.execution_layers[0].data_sources[1]
        self.workflow.mco.kpis.append(KPISpecification(name='T1'))
        self.workflow.mco.kpis.append(KPISpecification())

        self.available_variables = [
            Variable(name='T1', type='PRESSURE')
        ]

        self.kpi_view = KPISpecificationView(
            model=self.workflow.mco,
            kpi_name_options=self.available_variables
        )

    def test_kpi_view_init(self):
        self.assertEqual(2, len(self.kpi_view.model_views))
        self.assertEqual(
            self.kpi_view.model_views[0].selected_variable,
            self.available_variables[0]
        )
        self.assertEqual(
            'KPI: T1 (MINIMISE)', self.kpi_view.model_views[0].label
        )
        self.assertEqual(
            'KPI', self.kpi_view.model_views[1].label
        )
        self.assertEqual("MCO KPIs", self.kpi_view.label)
        self.assertEqual(
            self.kpi_view.selected_model_view,
            self.kpi_view.model_views[0]
        )

    def test_label(self):

        kpi_model_view = self.kpi_view.model_views[1]

        self.assertEqual(2, len(kpi_model_view.available_variables))
        self.assertEqual(
            'T1', kpi_model_view.available_variables[1].name
        )
        self.assertEqual('KPI', kpi_model_view.label)

        variable = kpi_model_view.available_variables[1]
        kpi_model_view.selected_variable = variable

        self.assertEqual("KPI: T1 (MINIMISE)", kpi_model_view.label)

        self.workflow.mco.kpis[1].objective = 'MAXIMISE'

        self.assertEqual("KPI: T1 (MAXIMISE)", kpi_model_view.label)

    def test_name_change(self):

        kpi_model_view = self.kpi_view.model_views[0]
        variable = kpi_model_view.available_variables[1]
        kpi_model_view.selected_variable = variable

        with self.assertTraitChanges(kpi_model_view, 'label', count=0):
            self.workflow.mco.kpis[0].name = 'T1'
            self.assertEqual("KPI: T1 (MINIMISE)", kpi_model_view.label)

        with self.assertTraitChanges(kpi_model_view, 'label', count=1):
            kpi_model_view.selected_variable.name = 'V1'
            self.assertEqual('KPI: V1 (MINIMISE)', kpi_model_view.label)

    def test_add_kpi(self):

        self.assertEqual(1, len(self.kpi_view.kpi_name_options))
        kpi_model_view = self.kpi_view.model_views[0]

        self.kpi_view._add_kpi_button_fired()
        self.assertEqual(3, len(self.workflow.mco.kpis))
        self.assertEqual(3, len(self.kpi_view.model_views))

        kpi_model_view = self.kpi_view.model_views[2]
        variable = kpi_model_view.available_variables[1]
        kpi_model_view.selected_variable = variable
        self.assertEqual('KPI: T1 (MINIMISE)', kpi_model_view.label)
        self.assertEqual(self.kpi_view.selected_model_view,
                         kpi_model_view)

    def test_remove_kpi(self):

        kpi_model_view = self.kpi_view.model_views[1]
        self.kpi_view.selected_model_view = kpi_model_view
        self.kpi_view._remove_kpi_button_fired()

        self.assertEqual(1, len(self.workflow.mco.kpis))
        self.assertEqual(1, len(self.kpi_view.model_views))

        self.kpi_view._add_kpi_button_fired()
        self.kpi_view._add_kpi_button_fired()
        self.assertEqual(3, len(self.workflow.mco.kpis))
        self.assertEqual(self.kpi_view.model_views[2],
                         self.kpi_view.selected_model_view)

        self.kpi_view.selected_model_view = self.kpi_view.model_views[0]
        kpi_model_view = self.kpi_view.model_views[1]
        self.kpi_view._remove_kpi_button_fired()
        self.assertEqual(self.kpi_view.model_views[0],
                         kpi_model_view)
        self.assertEqual(self.kpi_view.model_views[0],
                         self.kpi_view.selected_model_view)
        self.kpi_view._remove_kpi_button_fired()
        self.kpi_view.selected_model_view = self.kpi_view.model_views[-1]
        self.assertEqual(self.kpi_view.model_views[0],
                         self.kpi_view.selected_model_view)

    def test_verify_workflow_event(self):

        kpi_model_view = self.kpi_view.model_views[0]
        with self.assertTraitChanges(
                self.kpi_view, 'verify_workflow_event', count=1):
            variable = kpi_model_view.available_variables[0]
            kpi_model_view.selected_variable = variable
            self.assertEqual('', kpi_model_view.model.name)

        with self.assertTraitChanges(
                self.kpi_view, 'verify_workflow_event', count=0):
            kpi_model_view.model.name = 'T2'
            self.assertEqual('', kpi_model_view.model.name)

    def test__kpi_names_check(self):

        self.workflow.mco.kpis[0].name = 'T1'
        error_message = self.kpi_view.verify()

        self.assertEqual(0, len(error_message))
        kpi_model_view = self.kpi_view.model_views[1]
        self.kpi_view.kpi_name_options.append(
            Variable(name='T2', type='PRESSURE')
        )

        self.assertEqual(2, len(self.kpi_view.kpi_name_options))
        self.assertEqual(3, len(kpi_model_view.available_variables))

        variable = kpi_model_view.available_variables[2]
        kpi_model_view.selected_variable = variable
        self.assertEqual('T2', kpi_model_view.model.name)

        error_message = self.kpi_view.verify()
        self.assertEqual(0, len(error_message))

        kpi_model_view = self.kpi_view.model_views[0]
        variable = kpi_model_view.available_variables[2]
        kpi_model_view.selected_variable = variable
        error_message = self.kpi_view.verify()

        self.assertEqual(1, len(error_message))
        self.assertIn(
            'Two or more KPIs have a duplicate name',
            error_message[0].local_error,
        )
