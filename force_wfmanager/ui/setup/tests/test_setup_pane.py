#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

from unittest import TestCase

from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant

from force_bdss.api import ExecutionLayer, Workflow
from force_bdss.tests.probe_classes.mco import ProbeParameter

from force_wfmanager.tests.probe_classes import (
    ProbeWfManager
)
from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask


class TestSetupPane(GuiTestAssistant, TestCase):

    def setUp(self):
        super(TestSetupPane, self).setUp()
        self.wfmanager = ProbeWfManager()
        self.wfmanager.run()

        self.setup_pane = self.wfmanager.windows[0].central_pane
        self.side_pane = self.wfmanager.windows[0].tasks[0].side_pane
        self.system_state = self.wfmanager.windows[0].tasks[0].system_state
        self.factory_registry = (self.wfmanager.windows[0]
                                 .tasks[0].factory_registry)

        self.model = (self.factory_registry
                      .data_source_factories[0].create_model())

        #: Store these data source models in an exectution layer
        self.data_sources = [self.model]
        self.execution_layer = ExecutionLayer(
            data_sources=self.data_sources
        )

        #: Create MCO model to store some variables
        self.mco_model = self.factory_registry.mco_factories[0].create_model(
        )
        self.mco_model.parameters.append(ProbeParameter(None, name='P1',
                                                        type='PRESSURE'))
        self.mco_model.parameters.append(ProbeParameter(None, name='P2',
                                                        type='PRESSURE'))

        #: Set up workflow containing 1 execution layer with 1
        #: data sources and 2 MCO parameters
        self.workflow = Workflow(
            mco_model=self.mco_model,
            execution_layers=[self.execution_layer]
        )

        self.side_pane.workflow_model = self.workflow

        self.workflow_tree = self.side_pane.workflow_tree
        self.workflow_view = self.side_pane.workflow_tree.workflow_view

    def tearDown(self):
        for plugin in self.wfmanager:
            self.wfmanager.remove_plugin(plugin)
        self.wfmanager.exit()
        super(TestSetupPane, self).tearDown()

    def test_init_setup_pane(self):
        self.assertEqual(
            self.system_state,
            self.setup_pane.system_state)

        self.assertIsNotNone(self.system_state.selected_view)
        self.assertIsNone(self.system_state.entity_creator)
        self.assertIsNone(self.system_state.add_new_entity)
        self.assertEqual(
            1, len(self.workflow_view.process_view[0]
                   .execution_layer_views))
        self.assertEqual(
            1, len(self.workflow_view.process_view[0]
                   .execution_layer_views[0].data_source_views))
        self.assertEqual(self.setup_pane.system_state,
                         self.side_pane.system_state)
        self.assertEqual(self.setup_pane.system_state,
                         self.system_state)
        self.assertTrue(self.setup_pane.main_view_visible)
        self.assertTrue(self.setup_pane.ui_enabled)

    def test_mco_view(self):

        self.workflow_tree.mco_selected(self.workflow_view)

        self.assertEqual(
            'MCO',
            self.system_state.selected_factory_name,
        )

        self.assertFalse(self.setup_pane.mco_view_visible)
        self.assertTrue(self.setup_pane.factory_view_visible)
        self.assertFalse(self.setup_pane.instance_view_visible)

    def test_optimizer_view(self):
        mco_view = (
            self.workflow_view.mco_view[0]
        )
        self.workflow_tree.mco_optimizer_selected(mco_view)

        self.assertEqual(
            'None',
            self.system_state.selected_factory_name,
        )

        self.assertFalse(self.setup_pane.mco_view_visible)
        self.assertFalse(self.setup_pane.factory_view_visible)
        self.assertTrue(self.setup_pane.instance_view_visible)

    def test_parameter_view(self):
        mco_view = (
            self.workflow_view.mco_view[0]
        )
        self.workflow_tree.mco_parameters_selected(mco_view)

        self.assertEqual(
            'MCO Parameters',
            self.system_state.selected_factory_name,
        )

        self.assertTrue(self.setup_pane.mco_view_visible)
        self.assertFalse(self.setup_pane.factory_view_visible)
        self.assertFalse(self.setup_pane.instance_view_visible)

    def test_kpi_view(self):
        mco_view = (
            self.workflow_view.mco_view[0]
        )
        self.workflow_tree.mco_kpis_selected(mco_view)

        self.assertEqual(
            'MCO KPIs',
            self.system_state.selected_factory_name,
        )

        self.assertTrue(self.setup_pane.mco_view_visible)
        self.assertFalse(self.setup_pane.factory_view_visible)
        self.assertFalse(self.setup_pane.instance_view_visible)

    def test_execution_layer_view(self):
        execution_layer_view = (
            self.workflow_view.process_view[0]
            .execution_layer_views[0]
        )
        self.workflow_tree.execution_layer_selected(execution_layer_view)

        self.assertEqual(
            'Data Source',
            self.system_state.selected_factory_name
        )

        self.assertFalse(self.setup_pane.mco_view_visible)
        self.assertTrue(self.setup_pane.factory_view_visible)
        self.assertFalse(self.setup_pane.instance_view_visible)

    def test_data_source_view(self):
        data_source_view = (
            self.workflow_view.process_view[0]
            .execution_layer_views[0].data_source_views[0]
        )
        self.workflow_tree.data_source_selected(data_source_view)

        self.assertEqual(
            'None', self.system_state.selected_factory_name
        )

        self.assertFalse(self.setup_pane.mco_view_visible)
        self.assertFalse(self.setup_pane.factory_view_visible)
        self.assertTrue(self.setup_pane.instance_view_visible)

    def test_selected_view_editable(self):
        execution_layer_view = (
            self.workflow_view.process_view[0].execution_layer_views[0]
        )

        self.system_state.selected_view = execution_layer_view
        self.assertFalse(self.setup_pane.selected_view_editable)

        data_source_view = (
            self.workflow_view.process_view[0].execution_layer_views[0]
            .data_source_views[0]
        )

        self.system_state.selected_view = data_source_view
        self.assertTrue(self.setup_pane.selected_view_editable)

    def test_add_entity_button(self):
        self.assertEqual(
            1, len(self.workflow_view.process_view[0].execution_layer_views)
        )

        self.workflow_tree.process_selected(self.workflow_view.process_view[0])

        self.setup_pane.add_new_entity_btn = True

        self.assertEqual(
            2, len(self.workflow_view.process_view[0].execution_layer_views)
        )

        self.assertEqual(
            0, len(self.workflow_view.communicator_view[0]
                   .notification_listener_views)
        )

        self.workflow_tree.communicator_selected(
            self.workflow_view.communicator_view[0]
        )
        self.system_state.entity_creator.model = (
            self.factory_registry.notification_listener_factories[0]
            .create_model()
        )
        self.setup_pane.add_new_entity_btn = True

        self.assertIsNotNone(self.system_state.entity_creator)
        self.assertEqual(
            1, len(self.workflow_view.communicator_view[0]
                   .notification_listener_views)
        )

    def test_remove_entity_button(self):

        execution_layer_view = (
            self.workflow_view.process_view[0].execution_layer_views[0]
        )

        self.workflow_tree.execution_layer_selected(execution_layer_view)

        self.setup_pane.remove_entity_btn = True

        self.assertEqual(
            0,
            len(self.workflow_view.process_view[0].execution_layer_views)
        )

    def test_sync_error_message(self):

        execution_layer_view = (
            self.workflow_view.process_view[0].execution_layer_views[0]
        )

        self.system_state.selected_view = execution_layer_view

        self.assertEqual(
            execution_layer_view.error_message,
            self.setup_pane.error_message
        )

        self.system_state.selected_view.error_message = 'New error'

        self.assertEqual(
            'New error',
            self.setup_pane.error_message
        )

    def test_console_ns(self):
        namespace = self.setup_pane._console_ns_default()

        self.assertIsInstance(
            namespace['task'],
            WfManagerSetupTask
        )
        self.assertIsInstance(
            namespace['app'],
            ProbeWfManager
        )
