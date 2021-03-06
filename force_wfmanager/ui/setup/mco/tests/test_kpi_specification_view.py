#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

import unittest

from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import OutputSlotInfo, KPISpecification

from force_wfmanager.ui.setup.mco.kpi_specification_view import \
    KPISpecificationView
from force_wfmanager.utils.tests.test_variable_names_registry import \
    get_basic_variable_names_registry


class TestKPISpecificationView(unittest.TestCase, UnittestTools):

    def setUp(self):
        self.registry = get_basic_variable_names_registry()
        self.workflow = self.registry.workflow
        self.param1 = self.workflow.mco_model.parameters[0]
        self.param2 = self.workflow.mco_model.parameters[1]
        self.param3 = self.workflow.mco_model.parameters[2]
        self.data_source1 = self.workflow.execution_layers[0].data_sources[0]
        self.data_source2 = self.workflow.execution_layers[0].data_sources[1]
        self.workflow.mco_model.kpis.append(KPISpecification())

        self.kpi_view = KPISpecificationView(
            model=self.workflow.mco_model,
            variable_names_registry=self.registry
        )

    def test_kpi_view_init(self):
        self.assertEqual(1, len(self.kpi_view.kpi_names))
        self.assertEqual(1, len(self.kpi_view.model_views))
        self.assertEqual('KPI', self.kpi_view.model_views[0].label)
        self.assertEqual("MCO KPIs", self.kpi_view.label)
        self.assertEqual(
            self.kpi_view.selected_model_view,
            self.kpi_view.model_views[0]
        )

    def test_label(self):

        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]

        self.assertEqual([('T1', 'PRESSURE')],
                         self.registry.data_source_outputs)
        self.assertEqual(
            ['T1'], self.kpi_view.model_views[0]._combobox_values
        )
        self.assertEqual('KPI', self.kpi_view.model_views[0].label)

        self.workflow.mco_model.kpis[0].name = 'T1'

        self.assertEqual(
            "KPI: T1 (MINIMISE)",
            self.kpi_view.model_views[0].label
        )

        self.workflow.mco_model.kpis[0].objective = 'MAXIMISE'

        self.assertEqual(
            "KPI: T1 (MAXIMISE)",
            self.kpi_view.model_views[0].label
        )

    def test_name_change(self):

        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        kpi_model_view = self.kpi_view.model_views[0]

        with self.assertTraitChanges(kpi_model_view, 'label', count=0):
            self.assertEqual('KPI', kpi_model_view.label)

        with self.assertTraitChanges(kpi_model_view, 'label', count=1):
            self.workflow.mco_model.kpis[0].name = 'T1'
            self.assertEqual('KPI: T1 (MINIMISE)', kpi_model_view.label)

    def test_add_kpi(self):

        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        self.assertEqual(1, len(self.kpi_view.kpi_name_options))

        self.kpi_view._add_kpi_button_fired()
        self.assertEqual(2, len(self.workflow.mco_model.kpis))
        self.assertEqual(2, len(self.kpi_view.model_views))

        kpi_model_view = self.kpi_view.model_views[1]
        kpi_model_view.model.name = 'T1'
        self.assertEqual('KPI: T1 (MINIMISE)', kpi_model_view.label)
        self.assertEqual(self.kpi_view.selected_model_view,
                         kpi_model_view)

    def test_remove_kpi(self):
        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        kpi_model_view = self.kpi_view.model_views[0]
        self.kpi_view.selected_model_view = kpi_model_view
        self.kpi_view._remove_kpi_button_fired()

        self.assertEqual(0, len(self.workflow.mco_model.kpis))
        self.assertEqual(0, len(self.kpi_view.model_views))
        self.assertIsNone(self.kpi_view.selected_model_view)

        self.kpi_view._add_kpi_button_fired()
        self.kpi_view._add_kpi_button_fired()
        self.kpi_view._add_kpi_button_fired()
        self.assertEqual(3, len(self.workflow.mco_model.kpis))
        self.assertEqual(self.kpi_view.model_views[2],
                         self.kpi_view.selected_model_view)

        self.kpi_view.selected_model_view = self.kpi_view.model_views[0]
        self.kpi_view._remove_kpi_button_fired()
        self.assertEqual(self.kpi_view.model_views[0],
                         self.kpi_view.selected_model_view)
        self.kpi_view._remove_kpi_button_fired()
        self.kpi_view.selected_model_view = self.kpi_view.model_views[-1]
        self.assertEqual(self.kpi_view.model_views[0],
                         self.kpi_view.selected_model_view)

    def test_verify_workflow_event(self):
        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        kpi_model_view = self.kpi_view.model_views[0]
        with self.assertTraitChanges(
                self.kpi_view, 'verify_workflow_event', count=1):
            kpi_model_view.model.name = 'T1'
        with self.assertTraitChanges(
                self.kpi_view, 'verify_workflow_event', count=2):
            kpi_model_view.model.name = 'T2'

    def test__kpi_names_check(self):

        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        self.workflow.mco_model.kpis[0].name = 'T1'
        error_message = self.kpi_view.verify_model_names()
        self.assertEqual(0, len(error_message))

        self.data_source2.output_slot_info = [OutputSlotInfo(name='T2')]
        self.kpi_view._add_kpi_button_fired()
        self.workflow.mco_model.kpis[1].name = 'T2'
        error_message = self.kpi_view.verify_model_names()
        self.assertEqual(0, len(error_message))

        self.workflow.mco_model.kpis[0].name = 'T2'
        error_message = self.kpi_view.verify_model_names()
        self.assertEqual(1, len(error_message))
        self.assertIn(
            'Two or more KPIs have a duplicate name',
            error_message[0].local_error,
        )

    def test_variable_names_registry(self):

        self.kpi_view.variable_names_registry = None
        self.assertEqual(0, len(self.kpi_view.kpi_name_options))
        self.assertEqual(1, len(self.kpi_view.kpi_names))
        self.assertEqual(1, len(self.kpi_view.model_views))
