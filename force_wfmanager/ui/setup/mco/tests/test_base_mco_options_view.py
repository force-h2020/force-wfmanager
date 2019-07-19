import unittest

from traits.testing.unittest_tools import UnittestTools

from force_wfmanager.ui.setup.mco.base_mco_options_view import \
    BaseMCOOptionsView
from force_wfmanager.utils.tests.test_variable_names_registry import \
    get_basic_variable_names_registry
from force_wfmanager.tests.dummy_classes.dummy_mco_options_view import \
    DummyBaseMCOOptionsView


class TestBaseMCOOptionsView(unittest.TestCase, UnittestTools):

    def setUp(self):
        self.registry = get_basic_variable_names_registry()
        self.workflow = self.registry.workflow
        self.param1 = self.workflow.mco.parameters[0]
        self.param2 = self.workflow.mco.parameters[1]
        self.param3 = self.workflow.mco.parameters[2]
        self.data_source1 = self.workflow.execution_layers[0].data_sources[0]
        self.data_source2 = self.workflow.execution_layers[0].data_sources[1]

        self.mco_options_view = DummyBaseMCOOptionsView(
            model=self.workflow.mco,
            variable_names_registry=self.registry
        )

    def test_mco_options_view_init(self):

        self.assertIsNone(self.mco_options_view.selected_model_view)
        self.assertEqual(0, len(self.mco_options_view.model_views))

    def test___model_views_default_error(self):

        with self.assertRaises(NotImplementedError):
            mco_options_view = BaseMCOOptionsView()
            self.assertEqual(0, len(mco_options_view.model_views))
