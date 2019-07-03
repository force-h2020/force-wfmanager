import unittest

from traits.api import Int

from force_bdss.tests.dummy_classes.extension_plugin import \
    DummyExtensionPlugin
from force_bdss.tests.probe_classes.mco import ProbeParameterFactory
from force_bdss.api import BaseMCOParameterFactory, BaseMCOParameter
from force_wfmanager.ui.setup.mco.mco_parameter_model_view import \
    MCOParameterModelView


class ProbeParameter(BaseMCOParameter):

    new_data = Int(5)


class ProbeParameterFactory(BaseMCOParameterFactory):
    def get_name(self):
        return "Probe parameter"

    def get_identifier(self):
        return "probe_mco_parameter"

    def get_description(self):
        return "Probe parameter"

    def get_model_class(self):
        return ProbeParameter


class TestMCOParameterModelViewTest(unittest.TestCase):

    def setUp(self):
        self.plugin = DummyExtensionPlugin()
        self.mco_factory = self.plugin.mco_factories[0]
        self.mco_param_mv = MCOParameterModelView(
            model=ProbeParameterFactory(self.mco_factory).create_model())

    def test_mco_parameter_mv_init(self):
        self.assertEqual(self.mco_param_mv.label,
                         "Probe parameter")

    def test_mco_parameter_label(self):
        self.mco_param_mv.model.name = 'P1'
        self.mco_param_mv.model.type = 'PRESSURE'
        self.assertEqual(self.mco_param_mv.label,
                         "Probe parameter: PRESSURE P1")

    def test_mco_parameter_traits_view(self):
        self.mco_param_mv.model.new_data = 5
        self.mco_param_mv.default_traits_view()
