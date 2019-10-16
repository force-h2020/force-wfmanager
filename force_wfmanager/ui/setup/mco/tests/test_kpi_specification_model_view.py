import unittest

from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import KPISpecification

from force_wfmanager.ui.setup.mco.kpi_specification_model_view import \
    KPISpecificationModelView
from force_wfmanager.ui.ui_utils import model_info
from force_wfmanager.utils.variable_names_registry import Variable


class TestKPISpecificationModelView(unittest.TestCase, UnittestTools):

    def setUp(self):
        self.variable = Variable(
            type='PRESSURE',
            layer=0,
            name='T1'
        )
        self.kpi_model_view = KPISpecificationModelView(
            model=KPISpecification(),
            available_variables=[self.variable],
            selected_variable=self.variable
        )

    def test_kpi_model_view_init(self):
        self.assertIsNotNone(self.kpi_model_view.model)
        self.assertIsNotNone(self.kpi_model_view.selected_variable)

        self.assertEqual('T1', self.kpi_model_view.model.name)
        self.assertEqual(
            "KPI: T1 (MINIMISE)",
            self.kpi_model_view.label
        )
        self.assertTrue(self.kpi_model_view.valid)

    def test_kpi_model_update(self):
        # Should prevent direct changes to the model name
        self.kpi_model_view.model.name = 'V1'
        self.assertEqual('T1', self.kpi_model_view.model.name)
        self.assertEqual(
            "KPI: T1 (MINIMISE)",
            self.kpi_model_view.label
        )

        # UI can alter other attributes, however
        self.kpi_model_view.model.objective = 'MAXIMISE'
        self.assertEqual(
            "KPI: T1 (MAXIMISE)",
            self.kpi_model_view.label
        )

    def test_kpi_label(self):
        self.kpi_model_view.selected_variable.name = 'V1'
        self.kpi_model_view.selected_variable.type = 'VOLUME'

        self.assertEqual('V1', self.kpi_model_view.model.name)
        self.assertEqual(
            "KPI: V1 (MINIMISE)",
            self.kpi_model_view.label,
        )

    def test_verify_workflow_event(self):
        new_variable = Variable(
            type='PRESSURE',
            layer=0,
            name='T2'
        )
        self.kpi_model_view.available_variables.append(
            new_variable
        )
        with self.assertTraitChanges(
                self.kpi_model_view, 'verify_workflow_event', count=2):
            self.kpi_model_view.selected_variable = new_variable
            self.assertEqual('T2', self.kpi_model_view.model.name)
        with self.assertTraitChanges(
                self.kpi_model_view, 'verify_workflow_event', count=2):
            self.kpi_model_view.model.name = 'T1'
            self.assertEqual('T2', self.kpi_model_view.model.name)

    def test__check_kpi_name(self):
        self.assertTrue(self.kpi_model_view.valid)
        self.kpi_model_view.available_variables.remove(
            self.kpi_model_view.selected_variable
        )
        self.assertIsNone(self.kpi_model_view.selected_variable)
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

    def test_traits_view(self):
        info = model_info(self.kpi_model_view)
        self.assertIn('selected_variable', info)
