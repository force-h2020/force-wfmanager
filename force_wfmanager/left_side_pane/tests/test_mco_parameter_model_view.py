import unittest

from force_bdss.tests.dummy_classes.extension_plugin import \
    DummyExtensionPlugin
from force_bdss.tests.probe_classes.mco import ProbeParameterFactory

from force_wfmanager.left_side_pane.mco_parameter_model_view import \
    MCOParameterModelView


class TestMCOParameterModelViewTest(unittest.TestCase):
    def setUp(self):
        self.plugin = DummyExtensionPlugin()
        self.mco_factory = self.plugin.mco_factories[0]
        self.mco_param_mv = MCOParameterModelView(
            model=ProbeParameterFactory(self.mco_factory).create_model())

    def test_mco_parameter_mv_init(self):
        self.assertEqual(self.mco_param_mv.label,
                         "Probe parameter (No Name, No Type)")

    def test_mco_parameter_label(self):
        self.mco_param_mv.model.name = 'P1'
        self.mco_param_mv.model.type = 'PRESSURE'
        self.assertEqual(self.mco_param_mv.label,
                         "Probe parameter (Name: P1, Type: PRESSURE)")
