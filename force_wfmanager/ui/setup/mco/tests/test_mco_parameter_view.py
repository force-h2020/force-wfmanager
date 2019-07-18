import unittest
from traits.testing.unittest_tools import UnittestTools

from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin
from force_bdss.tests.probe_classes.mco import ProbeParameterFactory

from force_wfmanager.ui.setup.mco.mco_parameter_view import \
    MCOParameterModelView, MCOParameterView
from force_wfmanager.utils.tests.test_variable_names_registry import \
    get_basic_variable_names_registry


class TestMCOParameterModelView(unittest.TestCase, UnittestTools):

    def setUp(self):
        self.plugin = ProbeExtensionPlugin()
        self.mco_factory = self.plugin.mco_factories[0]
        self.parameter_factory = ProbeParameterFactory(self.mco_factory)
        self.parameter_model_view = MCOParameterModelView(
            model=self.parameter_factory.create_model()
        )

    def test_mco_parameter_view_init(self):
        self.assertEqual(
            "Probe parameter", self.parameter_model_view.label,
        )
        self.assertEqual(self.parameter_model_view.label,
                         "Probe parameter")

    def test_mco_parameter_label(self):
        self.parameter_model_view.model.name = 'P1'
        self.parameter_model_view.model.type = 'PRESSURE'
        self.assertEqual(self.parameter_model_view.label,
                         "Probe parameter: PRESSURE P1")

    def test_verify_workflow_event(self):
        with self.assertTraitChanges(
                self.parameter_model_view, 'verify_workflow_event', count=1):
            self.parameter_model_view.model.name = 'another'

    def test_traits_view(self):
        trait_view = self.parameter_model_view.trait_view()
        trait_view_repr = trait_view.content.__repr__()

        self.assertIn(
            'name',
            trait_view_repr,
        )
        self.assertIn(
            'type',
            trait_view_repr,
        )
        self.assertIn(
            'model',
            trait_view_repr,
        )


class TestMCOParameterView(unittest.TestCase, UnittestTools):

    def setUp(self):
        self.registry = get_basic_variable_names_registry()
        self.workflow = self.registry.workflow
        self.param1 = self.workflow.mco.parameters[0]
        self.param2 = self.workflow.mco.parameters[1]
        self.param3 = self.workflow.mco.parameters[2]
        self.data_source1 = self.workflow.execution_layers[0].data_sources[0]
        self.data_source2 = self.workflow.execution_layers[0].data_sources[1]

        self.parameter_view = MCOParameterView(
            model=self.workflow.mco,
            variable_names_registry=self.registry
        )

    def test_mco_parameter_view_init(self):
        self.assertEqual(
            "Probe parameter",
            self.parameter_view.parameter_model_views[0].label,
        )
        self.assertIsNotNone(self.parameter_view.parameter_entity_creator)
        self.assertEqual(
            self.parameter_view.selected_parameter,
            self.parameter_view.parameter_model_views[0]
        )

    def test_parameter_entity_creator(self):

        mco_model = self.parameter_view.model
        self.parameter_view.model = None
        self.assertIsNone(self.parameter_view.parameter_entity_creator)
        self.assertEqual(0, len(self.parameter_view.parameter_model_views))
        self.assertEqual(None, self.parameter_view.selected_parameter)

        self.parameter_view.model = mco_model
        self.assertIsNotNone(self.parameter_view.parameter_entity_creator)

    def test_add_parameter(self):

        self.parameter_view.parameter_entity_creator.selected_factory = (
            self.parameter_view.parameter_entity_creator.factories[0]
        )

        self.parameter_view._add_parameter_button_fired()

        self.assertEqual(4, len(self.workflow.mco.parameters))
        self.assertEqual(4, len(self.parameter_view.parameter_model_views))

        parameter_model_view = self.parameter_view.parameter_model_views[3]
        self.assertEqual(
            "Probe parameter",
            parameter_model_view.label,
        )
        self.assertEqual(
            self.parameter_view.selected_parameter,
            self.parameter_view.parameter_model_views[3]
        )

        self.parameter_view._dclick_add_parameter(None)
        self.assertEqual(5, len(self.workflow.mco.parameters))

    def test_remove_parameter(self):

        parameter_model_view = self.parameter_view.parameter_model_views[1]
        self.parameter_view.selected_parameter = parameter_model_view
        self.parameter_view._remove_parameter_button_fired()

        self.assertEqual(2, len(self.workflow.mco.parameters))
        self.assertEqual(2, len(self.parameter_view.parameter_model_views))
        self.assertEqual(
            self.parameter_view.selected_parameter,
            self.parameter_view.parameter_model_views[0]
        )

        self.parameter_view._remove_parameter_button_fired()
        self.parameter_view._remove_parameter_button_fired()

        self.assertEqual(
            None,
            self.parameter_view.selected_parameter
        )

    def test_verify_workflow_event(self):
        parameter_model_view = self.parameter_view.parameter_model_views[0]

        with self.assertTraitChanges(
                self.parameter_view, 'verify_workflow_event', count=1):
            parameter_model_view.model.name = 'another'
