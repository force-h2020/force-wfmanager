import unittest

from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import KPISpecification

from force_wfmanager.tests.dummy_classes.dummy_mco_options_view import \
    DummyBaseMCOOptionsModelView
from force_wfmanager.ui.setup.mco.base_mco_options_model_view import \
    BaseMCOOptionsModelView


class TestBaseMCOOptionsModelView(unittest.TestCase, UnittestTools):

    def setUp(self):

        self.mco_options_model_view = DummyBaseMCOOptionsModelView()

    def test_mco_options_model_view_init(self):

        self.assertIsNone(self.mco_options_model_view.model)
        self.assertTrue(self.mco_options_model_view.valid)

    def test__get_label_error(self):

        with self.assertRaises(NotImplementedError):
            mco_options_model_view = BaseMCOOptionsModelView()
            self.assertIsNotNone(mco_options_model_view.label)

    def test__check_model_name(self):

        self.mco_options_model_view._combobox_values = ['T1', 'T2']
        self.mco_options_model_view.model = KPISpecification(name='T1')

        self.mco_options_model_view._combobox_values.remove('T2')
        self.assertTrue(self.mco_options_model_view.valid)
        self.mco_options_model_view._combobox_values.remove('T1')

        self.assertEqual('', self.mco_options_model_view.model.name)
        error_message = self.mco_options_model_view.model.verify()
        self.assertIn(
            'KPI is not named',
            error_message[0].local_error
        )
