import unittest

from traits.testing.unittest_tools import UnittestTools

from force_wfmanager.ui.setup.mco.base_mco_options_model_view import (
    BaseMCOOptionsModelView
)
from force_wfmanager.utils.variable_names_registry import Variable


class TestBaseMCOOptionsModelView(unittest.TestCase, UnittestTools):

    def setUp(self):

        self.mco_options_model_view = BaseMCOOptionsModelView()

    def test_mco_options_model_view_init(self):

        self.assertIsNone(self.mco_options_model_view.model)
        self.assertIsInstance(
            self.mco_options_model_view.selected_variable,
            Variable
        )
        self.assertEqual(
            1, len(self.mco_options_model_view.available_variables)
        )
        self.assertIsInstance(
            self.mco_options_model_view.available_variables[0],
            Variable
        )
        self.assertTrue(self.mco_options_model_view.valid)

    def test__check_selected_model(self):
        variable1 = Variable(
            name='T1',
            type='PRESSURE'
        )

        self.mco_options_model_view.selected_variable = variable1
        self.assertEqual(
            self.mco_options_model_view._empty_variable,
            self.mco_options_model_view.selected_variable
        )

        self.mco_options_model_view.update_available_variables([variable1])
        self.assertEqual(
            2, len(self.mco_options_model_view.available_variables)
        )
        self.mco_options_model_view.selected_variable = variable1
        self.assertIsNotNone(self.mco_options_model_view.selected_variable)

        self.mco_options_model_view.available_variables = []
        self.assertEqual(
            self.mco_options_model_view._empty_variable,
            self.mco_options_model_view.selected_variable
        )
