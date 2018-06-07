import unittest

from force_bdss.tests.dummy_classes.extension_plugin import \
    DummyExtensionPlugin

from force_wfmanager.left_side_pane.mco_model_view import MCOModelView
from force_wfmanager.left_side_pane.mco_parameter_model_view import \
    MCOParameterModelView


class TestMCOModelView(unittest.TestCase):
    def setUp(self):
        plugin = DummyExtensionPlugin()
        factory = plugin.mco_factories[0]
        model = factory.create_model()
        parameter_factory = factory.parameter_factories()[0]
        model.parameters = [parameter_factory.create_model()]

        self.mco_mv = MCOModelView(model=model)

    def test_mco_parameter_representation(self):
        self.assertEqual(
            len(self.mco_mv.mco_parameters_mv), 1)
        self.assertIsInstance(
            self.mco_mv.mco_parameters_mv[0],
            MCOParameterModelView
        )

    def test_label(self):
        self.assertEqual(self.mco_mv.label, "Dummy MCO")
