import unittest
from traits.testing.unittest_tools import UnittestTools

from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin
from force_bdss.tests.probe_classes.mco import ProbeParameterFactory

from force_wfmanager.ui.setup.mco.mco_parameter_model_view import \
    MCOParameterModelView


class TestMCOParameterModelView(unittest.TestCase, UnittestTools):

    def setUp(self):
        self.plugin = ProbeExtensionPlugin()
        self.mco_factory = self.plugin.mco_factories[0]
        self.parameter_factory = ProbeParameterFactory(self.mco_factory)
        self.parameter_model_view = MCOParameterModelView(
            model=self.parameter_factory.create_model(),
            available_variables=[('P1', 'PRESSURE')]
        )

    def test_mco_parameter_view_init(self):
        self.assertEqual(
            "Probe parameter", self.parameter_model_view.label,
        )
        self.assertEqual(self.parameter_model_view.label,
                         "Probe parameter")

    def test_parameter_model_update(self):
        self.parameter_model_view.model.name = 'P1'
        self.assertEqual('PRESSURE', self.parameter_model_view.model.type)

    def test_mco_parameter_label(self):
        self.parameter_model_view.model.name = 'P1'
        self.assertEqual(self.parameter_model_view.label,
                         "Probe parameter: PRESSURE P1")

    def test_verify_workflow_event(self):
        self.parameter_model_view.available_variables.append(
            ('T2', 'PRESSURE')
        )
        with self.assertTraitChanges(
                self.parameter_model_view, 'verify_workflow_event', count=2):
            self.parameter_model_view.model.name = 'T2'
        with self.assertTraitChanges(
                self.parameter_model_view, 'verify_workflow_event', count=3):
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
