import unittest

from force_bdss.tests.dummy_classes.extension_plugin import \
    DummyExtensionPlugin
from force_bdss.tests.probe_classes.mco import ProbeParameterFactory
from force_wfmanager.ui.setup.mco.mco_parameter_view import \
    MCOParameterView


class TestMCOParameterModelViewTest(unittest.TestCase):

    def setUp(self):
        self.plugin = DummyExtensionPlugin()
        self.mco_factory = self.plugin.mco_factories[0]
        self.mco_parameter_view = MCOParameterView(
            model=ProbeParameterFactory(self.mco_factory).create_model()
        )

    def test_mco_parameter_view_init(self):
        self.assertEqual(self.mco_parameter_view.label,
                         "Probe parameter")

    def test_mco_parameter_label(self):
        self.mco_parameter_view.model.name = 'P1'
        self.mco_parameter_view.model.type = 'PRESSURE'
        self.assertEqual(self.mco_parameter_view.label,
                         "Probe parameter: PRESSURE P1")
