import unittest

from force_bdss.api import KPISpecification, Workflow
from force_bdss.tests.dummy_classes.extension_plugin import \
    DummyExtensionPlugin

from force_wfmanager.ui.setup.mco.mco_model_view import \
    MCOModelView
from force_wfmanager.ui.setup.mco.mco_parameter_model_view import \
    MCOParameterModelView

from force_wfmanager.utils.variable_names_registry import \
    VariableNamesRegistry
from force_wfmanager.utils.tests.test_variable_names_registry import \
    get_basic_variable_names_registry


class TestMCOModelView(unittest.TestCase):

    def setUp(self):
        plugin = DummyExtensionPlugin()
        factory = plugin.mco_factories[0]
        self.model = factory.create_model()
        parameter_factory = factory.parameter_factories[0]
        self.model.parameters = [parameter_factory.create_model()]
        self.variable_names_registry = VariableNamesRegistry(workflow=Workflow())
        self.mco_mv = MCOModelView(
            model=self.model,
            variable_names_registry=self.variable_names_registry)

    def test_mco_parameter_representation(self):
        self.assertEqual(
            len(self.mco_mv.parameter_model_views), 1)
        self.assertIsInstance(
            self.mco_mv.parameter_model_views[0],
            MCOParameterModelView
        )

    def test_label(self):
        self.assertEqual(self.mco_mv.label, "Dummy MCO")

    def test_add_kpi(self):
        kpi_spec = KPISpecification()
        self.mco_mv.add_kpi(kpi_spec)
        self.assertEqual(len(self.mco_mv.kpi_model_views), 1)
        self.assertEqual(self.mco_mv.kpi_model_views[0].model, kpi_spec)
        self.mco_mv.remove_kpi(kpi_spec)
        self.assertEqual(len(self.mco_mv.kpi_model_views), 0)
