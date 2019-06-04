import unittest

from force_bdss.api import KPISpecification
from force_bdss.tests.dummy_classes.extension_plugin import \
    DummyExtensionPlugin

from force_wfmanager.views.model_views.mco_model_view import MCOModelView
from force_wfmanager.views.model_views.mco_parameter_model_view import \
    MCOParameterModelView

from force_wfmanager.models.variable_names_registry import \
    VariableNamesRegistry
from force_wfmanager.models.workflow_tree import Workflow


class TestMCOModelView(unittest.TestCase):
    def setUp(self):
        plugin = DummyExtensionPlugin()
        factory = plugin.mco_factories[0]
        model = factory.create_model()
        parameter_factory = factory.parameter_factories[0]
        model.parameters = [parameter_factory.create_model()]
        var_names = VariableNamesRegistry(workflow=Workflow())
        self.mco_mv = MCOModelView(model=model,
                                   variable_names_registry=var_names)

    def test_mco_parameter_representation(self):
        self.assertEqual(
            len(self.mco_mv.mco_parameters_mv), 1)
        self.assertIsInstance(
            self.mco_mv.mco_parameters_mv[0],
            MCOParameterModelView
        )

    def test_label(self):
        self.assertEqual(self.mco_mv.label, "Dummy MCO")

    def test_add_kpi(self):
        kpi_spec = KPISpecification()
        self.mco_mv.add_kpi(kpi_spec)
        self.assertEqual(len(self.mco_mv.kpis_mv), 1)
        self.assertEqual(self.mco_mv.kpis_mv[0].model, kpi_spec)
        self.mco_mv.remove_kpi(kpi_spec)
        self.assertEqual(len(self.mco_mv.kpis_mv), 0)
