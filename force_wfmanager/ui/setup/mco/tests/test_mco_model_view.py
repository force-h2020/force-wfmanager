import unittest

from force_bdss.api import (
    KPISpecification, OutputSlotInfo
)

from force_wfmanager.ui.setup.mco.mco_view import \
    MCOView
from force_wfmanager.ui.setup.mco.mco_parameter_view import \
    MCOParameterView
from force_wfmanager.ui.setup.tests.template_test_case import \
    BaseTest


class TestMCOView(BaseTest):

    def setUp(self):
        super(TestMCOView, self).setUp()
        self.workflow.execution_layers[0].data_sources[0].output_slot_info \
            = [OutputSlotInfo(name='outputA')]
        self.workflow.execution_layers[0].data_sources[1].output_slot_info \
            = [OutputSlotInfo(name='outputB')]

        self.mco_view = MCOView(
            model=self.workflow.mco,
            variable_names_registry=self.variable_names_registry
        )

    def test_init_mco_view(self):
        self.assertEqual(0, len(self.mco_view.kpi_names))
        self.assertEqual(0, len(self.mco_view.kpi_views))
        self.assertEqual(2, len(self.mco_view.non_kpi_variables))

    def test_mco_parameter_representation(self):
        self.assertEqual(
            2, len(self.mco_view.parameter_views))
        self.assertIsInstance(
            self.mco_view.parameter_views[0],
            MCOParameterView,
        )

    def test_label(self):
        self.assertEqual("testmco", self.mco_view.label)

    def test_add_kpi(self):
        kpi_spec = KPISpecification()
        self.mco_view.add_kpi(kpi_spec)
        self.assertEqual(len(self.mco_view.kpi_views), 1)
        self.assertEqual(self.mco_view.kpi_views[0].model, kpi_spec)
        self.mco_view.remove_kpi(kpi_spec)
        self.assertEqual(len(self.mco_view.kpi_views), 0)
