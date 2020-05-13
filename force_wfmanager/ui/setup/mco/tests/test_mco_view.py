#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import (
    KPISpecification, OutputSlotInfo, BaseMCOParameter
)

from force_wfmanager.ui.setup.mco.mco_view import \
    MCOView
from force_wfmanager.ui.setup.mco.mco_parameter_view import (
    MCOParameterView
)
from force_wfmanager.ui.setup.mco.kpi_specification_view import (
    KPISpecificationView
)
from force_wfmanager.ui.setup.tests.wfmanager_base_test_case import \
    WfManagerBaseTestCase


class TestMCOView(WfManagerBaseTestCase, UnittestTools):

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
            model=self.workflow.mco_model,
            variable_names_registry=self.variable_names_registry
        )

        self.kpi_view = self.mco_view.kpi_view
        self.parameter_view = self.mco_view.parameter_view

    def test_init_mco_view(self):
        self.assertEqual(2, len(self.mco_view.mco_options))
        self.assertEqual(
            self.mco_view.mco_options[0],
            self.parameter_view
        )
        self.assertEqual(
            self.mco_view.mco_options[1],
            self.kpi_view
        )
        self.assertEqual(
            self.variable_names_registry,
            self.kpi_view.variable_names_registry
        )

        self.assertEqual(1, len(self.kpi_view.model_views))
        self.assertEqual(3, len(self.kpi_view.kpi_name_options))
        self.assertEqual(
            'outputA',
            self.kpi_view.model_views[0].model.name)
        self.assertEqual(
            'outputA',
            self.kpi_view.kpi_names[0])

        self.assertEqual(2, len(self.parameter_view.model_views))
        self.assertEqual(
            'P1',
            self.parameter_view.model_views[0].model.name)
        self.assertEqual(
            'P2',
            self.parameter_view.model_views[1].model.name)

    def test_label(self):
        self.assertEqual("testmco", self.mco_view.label)

    def test_add_kpi(self):
        kpi_spec = KPISpecification(name='outputB')

        self.kpi_view.add_kpi(kpi_spec)
        self.assertEqual(2, len(self.kpi_view.model_views))
        self.assertEqual(3, len(self.kpi_view.kpi_name_options))
        self.assertEqual(2, len(self.kpi_view.kpi_names))
        self.assertEqual(self.kpi_view.model_views[1].model, kpi_spec)
        self.assertEqual(
            'outputB',
            self.kpi_view.model_views[1].model.name)
        self.assertEqual(
            'KPI: outputB (MINIMISE)',
            self.kpi_view.model_views[1].label)
        self.assertEqual('outputB', self.kpi_view.kpi_names[1])

    def test_remove_kpi(self):
        kpi_spec = self.kpi_view.model_views[0].model
        self.kpi_view.remove_kpi(kpi_spec)
        self.assertEqual(0, len(self.kpi_view.model_views))
        self.assertEqual(3, len(self.kpi_view.kpi_name_options))
        self.assertEqual(0, len(self.kpi_view.kpi_names))

    def test_add_parameter(self):
        parameter = BaseMCOParameter(None, name='P3', type='PRESSURE')

        self.parameter_view.add_parameter(parameter)
        self.assertEqual(3, len(self.parameter_view.model_views))
        self.assertEqual(3, len(self.kpi_view.kpi_name_options))
        self.assertEqual(1, len(self.kpi_view.kpi_names))
        self.assertEqual(
            parameter, self.parameter_view.model_views[2].model)

    def test_remove_parameter(self):
        parameter = self.parameter_view.model_views[1].model
        self.parameter_view.remove_parameter(parameter)
        self.assertEqual(1, len(self.parameter_view.model_views))
        self.assertEqual(3, len(self.kpi_view.kpi_name_options))
        self.assertEqual(1, len(self.kpi_view.kpi_names))

    def test_verify_workflow_event(self):
        parameter_model_view = self.parameter_view.model_views[0]

        with self.assertTraitChanges(
                self.mco_view, 'verify_workflow_event', count=1):
            parameter_model_view.model.name = 'P2'

        kpi_model_view = self.kpi_view.model_views[0]
        with self.assertTraitChanges(
                self.mco_view, 'verify_workflow_event', count=2):
            kpi_model_view.model.name = 'another'

    def test_sync_mco_options(self):

        old_parameter_view = self.mco_view.parameter_view
        new_parameter_view = MCOParameterView(
            model=self.workflow.mco_model
        )

        self.mco_view.parameter_view = new_parameter_view

        self.assertEqual(
            new_parameter_view,
            self.mco_view.mco_options[0]
        )
        self.assertNotEqual(
            old_parameter_view,
            self.mco_view.mco_options[0]
        )

        old_kpi_view = self.mco_view.kpi_view
        new_kpi_view = KPISpecificationView(
            model=self.workflow.mco_model
        )

        self.mco_view.kpi_view = new_kpi_view

        self.assertEqual(
            new_kpi_view,
            self.mco_view.mco_options[1]
        )
        self.assertNotEqual(
            old_kpi_view,
            self.mco_view.mco_options[1]
        )
