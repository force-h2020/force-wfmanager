import unittest

from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import KPISpecification

from force_wfmanager.tests.dummy_classes.dummy_mco_options_view import \
    DummyBaseMCOOptionsModelView


class TestBaseMCOOptionsModelView(unittest.TestCase, UnittestTools):

    def setUp(self):

        self.mco_options_model_view = DummyBaseMCOOptionsModelView()

    def test_mco_options_model_view_init(self):

        self.assertIsNone(self.mco_options_model_view.model)
        self.assertTrue(self.mco_options_model_view.valid)

    def test__check_model_name(self):

        self.mco_options_model_view.available_variables = (
            [('T1', 'PRESSURE'), ('T2', 'PRESSURE')]
        )
        self.assertEqual(['T1', 'T2'],
                         self.mco_options_model_view._combobox_values)
        self.mco_options_model_view.model = KPISpecification(name='T1')

        self.mco_options_model_view.available_variables.remove(
            self.mco_options_model_view.available_variables[-1]
        )
        self.assertTrue(self.mco_options_model_view.valid)
        self.mco_options_model_view.available_variables.remove(
            self.mco_options_model_view.available_variables[0]
        )

        self.assertEqual('', self.mco_options_model_view.model.name)
        error_message = self.mco_options_model_view.model.verify()
        self.assertIn(
            'KPI is not named',
            error_message[0].local_error
        )
