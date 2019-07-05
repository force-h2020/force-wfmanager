import unittest

from force_bdss.api import (
    KPISpecification, OutputSlotInfo, BaseMCOParameter
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
            = [OutputSlotInfo(name='outputA'), OutputSlotInfo(name='outputX')]
        self.workflow.execution_layers[0].data_sources[1].output_slot_info \
            = [OutputSlotInfo(name='outputB')]

        self.mco_model.kpis.append(KPISpecification(
            name='outputA')
        )

        self.mco_view = MCOView(
            model=self.workflow.mco,
            variable_names_registry=self.variable_names_registry
        )

    def test_init_mco_view(self):
        self.assertEqual(1, len(self.mco_view.kpi_names))
        self.assertEqual(1, len(self.mco_view.kpi_views))
        self.assertEqual(2, len(self.mco_view.non_kpi_variables))
        self.assertEqual('outputA', self.mco_view.kpi_views[0].name)
        self.assertEqual('outputA', self.mco_view.kpi_names[0])

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
        kpi_spec = KPISpecification(name='outputB')

        self.mco_view.add_kpi(kpi_spec)
        self.assertEqual(2, len(self.mco_view.kpi_views))
        self.assertEqual(1, len(self.mco_view.non_kpi_variables))
        self.assertEqual(2, len(self.mco_view.kpi_names))
        self.assertEqual(self.mco_view.kpi_views[1].model, kpi_spec)
        self.assertEqual('outputB', self.mco_view.kpi_views[1].name)
        self.assertEqual('outputB', self.mco_view.kpi_names[1])

    def test_remove_kpi(self):
        kpi_spec = self.mco_view.kpi_views[0].model
        self.mco_view.remove_kpi(kpi_spec)
        self.assertEqual(0, len(self.mco_view.kpi_views))
        self.assertEqual(3, len(self.mco_view.non_kpi_variables))
        self.assertEqual(0, len(self.mco_view.kpi_names))

    def test_add_parameter(self):
        parameter = BaseMCOParameter(None, name='P3', type='PRESSURE')

        self.mco_view.add_parameter(parameter)
        self.assertEqual(3, len(self.mco_view.parameter_views))
        self.assertEqual(2, len(self.mco_view.non_kpi_variables))
        self.assertEqual(1, len(self.mco_view.kpi_names))
        self.assertEqual(
            parameter, self.mco_view.parameter_views[2].model)

    def test_remove_parameter(self):
        parameter = self.mco_view.parameter_views[1].model
        self.mco_view.remove_parameter(parameter)
        self.assertEqual(1, len(self.mco_view.parameter_views))
        self.assertEqual(2, len(self.mco_view.non_kpi_variables))
        self.assertEqual(1, len(self.mco_view.kpi_names))
