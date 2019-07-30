import unittest
from traits.testing.unittest_tools import UnittestTools

from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin
from force_bdss.tests.probe_classes.mco import ProbeParameterFactory

from force_wfmanager.ui.setup.mco.mco_parameter_model_view import \
    MCOParameterModelView
from force_wfmanager.ui.ui_utils import model_info
from force_wfmanager.utils.variable_names_registry import Variable


class TestMCOParameterModelView(unittest.TestCase, UnittestTools):

    def setUp(self):
        self.plugin = ProbeExtensionPlugin()
        self.mco_factory = self.plugin.mco_factories[0]
        self.parameter_factory = ProbeParameterFactory(self.mco_factory)
        self.variable = Variable(
            type='PRESSURE',
            layer=0,
            name='P1'
        )
        self.parameter_model_view = MCOParameterModelView(
            model=self.parameter_factory.create_model(),
            available_variables=[self.variable],
            selected_variable=self.variable
        )

    def test_mco_parameter_view_init(self):
        self.assertIsNotNone(self.parameter_model_view.model)
        self.assertIsNotNone(self.parameter_model_view.selected_variable)

        self.assertEqual('P1', self.parameter_model_view.model.name)
        self.assertEqual('PRESSURE', self.parameter_model_view.model.type)
        self.assertEqual(
            "Probe parameter: PRESSURE P1",
            self.parameter_model_view.label,
        )

    def test_parameter_model_update(self):
        # Should prevent direct changes to the model name and type
        self.parameter_model_view.model.name = 'V1'
        self.parameter_model_view.model.type = 'VOLUME'

        self.assertEqual('P1', self.parameter_model_view.model.name)
        self.assertEqual('PRESSURE', self.parameter_model_view.model.type)
        self.assertEqual(
            "Probe parameter: PRESSURE P1",
            self.parameter_model_view.label,
        )

    def test_mco_parameter_label(self):
        self.parameter_model_view.selected_variable.name = 'V1'
        self.parameter_model_view.selected_variable.type = 'VOLUME'

        self.assertEqual('V1', self.parameter_model_view.model.name)
        self.assertEqual('VOLUME', self.parameter_model_view.model.type)
        self.assertEqual(
            "Probe parameter: VOLUME V1",
            self.parameter_model_view.label,
        )

    def test_verify_workflow_event(self):
        new_variable = Variable(
            type='PRESSURE',
            layer=0,
            name='T2'
        )
        self.parameter_model_view.available_variables.append(
            new_variable
        )
        with self.assertTraitChanges(
                self.parameter_model_view, 'verify_workflow_event', count=2):
            self.parameter_model_view.selected_variable = new_variable
            self.assertEqual('T2', self.parameter_model_view.model.name)
        with self.assertTraitChanges(
                self.parameter_model_view, 'verify_workflow_event', count=2):
            self.parameter_model_view.model.name = 'T1'
            self.assertEqual('T2', self.parameter_model_view.model.name)

    def test_traits_view(self):
        info = model_info(self.parameter_model_view)
        self.assertIn('selected_variable', info)
        self.assertIn('model', info)
