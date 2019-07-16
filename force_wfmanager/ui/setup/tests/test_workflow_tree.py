from unittest import mock, TestCase

from force_bdss.api import (
    ExecutionLayer, Workflow, BaseMCOModel, KPISpecification
)
from force_wfmanager.ui.setup.tests.template_test_case import BaseTest

from force_wfmanager.ui.setup.workflow_tree import (
    WorkflowTree, TreeNodeWithStatus
)
from force_wfmanager.ui.setup.system_state import SystemState


class TestWorkflowTree(BaseTest):

    def setUp(self):
        super(TestWorkflowTree, self).setUp()
        data_sources = [
            self.factory_registry.data_source_factories[2].create_model(),
            self.factory_registry.data_source_factories[3].create_model()
        ]
        execution_layer = ExecutionLayer(
            data_sources=data_sources
        )
        self.workflow.execution_layers.append(execution_layer)
        self.workflow.mco.kpis.append(KPISpecification())

        self.system_state = SystemState()
        self.workflow_tree = WorkflowTree(
            model=self.workflow,
            _factory_registry=self.factory_registry,
            system_state=self.system_state
        )

    def test_ui_initialization(self):

        self.assertEqual(
            1, len(self.workflow_tree.workflow_view.mco_view)
        )
        self.assertEqual(
            1, len(self.workflow_tree.workflow_view.process_view)
        )
        self.assertEqual(
            1, len(self.workflow_tree.workflow_view.communicator_view)
        )

        process_view = self.workflow_tree.workflow_view.process_view[0]

        self.assertEqual(
            2, len(self.workflow_tree.workflow_view.model.execution_layers)
        )
        self.assertEqual(2, len(process_view.execution_layer_views))
        self.assertEqual(
            2, len(process_view.model.execution_layers[0]
                   .data_sources))
        self.assertEqual(
            2,
            len(process_view.execution_layer_views[0]
                .data_source_views))

        self.assertEqual(
            self.system_state,
            self.workflow_tree.system_state
        )

        self.assertIsNone(self.system_state.entity_creator)
        self.assertIsNone(self.system_state.add_new_entity)

    def test_workflow_selected(self):

        self.workflow_tree.workflow_selected(
            self.workflow_tree.workflow_view
        )
        self.assertEqual(
            'Workflow', self.system_state.selected_factory_name
        )
        self.assertIsNone(self.system_state.add_new_entity)
        self.assertIsNone(self.system_state.remove_entity)
        self.assertIsNone(self.system_state.entity_creator)

    def test_process_selected(self):

        process_view = (
            self.workflow_tree.workflow_view.process_view[0]
        )
        self.workflow_tree.process_selected(process_view)
        self.assertEqual(
            'Execution Layer', self.system_state.selected_factory_name
        )
        self.assertIsNotNone(self.system_state.add_new_entity)
        self.assertIsNone(self.system_state.remove_entity)
        self.assertIsNone(self.system_state.entity_creator)

    def test_execution_layer_selected(self):
        execution_layer_view = (
            self.workflow_tree.workflow_view.process_view[0]
            .execution_layer_views[0]
        )
        self.workflow_tree.execution_layer_selected(execution_layer_view)
        self.assertEqual(
            'Data Source', self.system_state.selected_factory_name
        )
        self.assertIsNotNone(self.system_state.add_new_entity)
        self.assertIsNotNone(self.system_state.remove_entity)
        self.assertIsNotNone(self.system_state.entity_creator)

    def test_data_source_selected(self):
        data_source_view = (
            self.workflow_tree.workflow_view.process_view[0]
            .execution_layer_views[0].data_source_views[0]
        )
        self.workflow_tree.data_source_selected(data_source_view)
        self.assertEqual(
            'None', self.system_state.selected_factory_name
        )
        self.assertIsNone(self.system_state.add_new_entity)
        self.assertIsNotNone(self.system_state.remove_entity)
        self.assertIsNone(self.system_state.entity_creator)

    def test_mco_selected(self):
        mco_view = (
            self.workflow_tree.workflow_view.mco_view[0]
        )
        self.workflow_tree.mco_selected(mco_view)
        self.assertEqual(
            'MCO', self.system_state.selected_factory_name
        )
        self.assertIsNotNone(self.system_state.add_new_entity)
        self.assertIsNone(self.system_state.remove_entity)
        self.assertIsNotNone(self.system_state.entity_creator)

    def test_mco_parameters_selected(self):
        mco_view = (
            self.workflow_tree.workflow_view.mco_view[0]
        )
        self.workflow_tree.mco_parameters_selected(mco_view)
        self.assertEqual(
            'MCO Parameters', self.system_state.selected_factory_name
        )

        self.assertIsNone(self.system_state.add_new_entity)
        self.assertIsNone(self.system_state.remove_entity)
        self.assertIsNone(self.system_state.entity_creator)

    def test_mco_kpis_selected(self):
        mco_view = (
            self.workflow_tree.workflow_view.mco_view[0]
        )
        self.workflow_tree.mco_kpis_selected(mco_view)
        self.assertEqual(
            'MCO KPIs', self.system_state.selected_factory_name
        )

        self.assertIsNone(self.system_state.add_new_entity)
        self.assertIsNone(self.system_state.remove_entity)
        self.assertIsNone(self.system_state.entity_creator)

    def test_new_mco(self):

        workflow_no_mco = Workflow()
        workflow_tree = WorkflowTree(
            model=workflow_no_mco,
            _factory_registry=self.factory_registry,
            system_state=self.system_state)

        self.assertIsNone(workflow_tree.workflow_view.model.mco)
        self.assertEqual(len(workflow_tree.workflow_view.mco_view), 0)

        workflow_tree.mco_selected(workflow_tree.workflow_view)

        self.system_state.entity_creator.model = (
            self.factory_registry.mco_factories[0].create_model()
        )
        self.system_state.add_new_entity()

        self.assertIsNotNone(workflow_tree.workflow_view.model.mco)
        self.assertEqual(len(workflow_tree.workflow_view.mco_view), 1)
        self.assertIsInstance(workflow_tree.workflow_view.model.mco,
                              BaseMCOModel)

    def test_delete_mco(self):

        self.assertIsNotNone(self.workflow_tree.model.mco)
        self.assertEqual(1, len(self.workflow_tree.workflow_view.mco_view))

        mco_view = self.workflow_tree.workflow_view.mco_view[0]

        self.workflow_tree.mco_optimizer_selected(mco_view)
        self.system_state.remove_entity()

        self.assertIsNone(self.workflow_tree.model.mco)
        self.assertEqual(0, len(self.workflow_tree.workflow_view.mco_view))

    def test_new_execution_layer(self):

        process_view = (
            self.workflow_tree.workflow_view.process_view[0]
        )
        self.workflow_tree.process_selected(process_view)

        self.system_state.add_new_entity()

        self.assertEqual(
            3, len(process_view.execution_layer_views)
        )

    def test_delete_execution_layer(self):
        process_view = (
            self.workflow_tree.workflow_view.process_view[0]
        )
        first_execution_layer = (
            process_view.execution_layer_views[0]
        )
        second_execution_layer = (
            process_view.execution_layer_views[1]
        )

        self.workflow_tree.execution_layer_selected(first_execution_layer)

        self.system_state.remove_entity()

        self.assertEqual(
            1, len(process_view.execution_layer_views))
        self.assertEqual(
            1, len(process_view.model.execution_layers))

        self.assertNotEqual(
            first_execution_layer,
            process_view.execution_layer_views[0]
        )
        self.assertEqual(
            len(second_execution_layer.data_source_views),
            len(process_view.execution_layer_views[0]
                .data_source_views)
        )

    def test_new_data_source(self):
        process_view = (
            self.workflow_tree.workflow_view.process_view[0]
        )
        execution_layer = (
            process_view.execution_layer_views[0]
        )

        self.assertEqual(len(execution_layer.data_source_views), 2)

        self.workflow_tree.execution_layer_selected(execution_layer)

        self.system_state.entity_creator.model = (
            self.factory_registry.data_source_factories[0].create_model()
        )

        self.system_state.add_new_entity()

        self.assertEqual(len(execution_layer.data_source_views), 3)

    def test_delete_data_source(self):
        process_view = (
            self.workflow_tree.workflow_view.process_view[0]
        )
        data_source = (
            process_view.execution_layer_views[0]
            .data_source_views[0]
        )

        self.workflow_tree.data_source_selected(data_source)

        self.system_state.remove_entity()

        self.assertEqual(
            1,
            len(process_view.execution_layer_views[0]
                .data_source_views)
            )
        self.assertEqual(
            1,
            len(process_view.model.execution_layers[0]
                .data_sources)
            )

    def test_new_notification_listener(self):
        communicator_view = (self.workflow_tree.workflow_view
                             .communicator_view[0])

        self.assertEqual(
            1, len(communicator_view.notification_listener_views)
        )
        self.assertEqual(
            1, len(self.workflow.notification_listeners)
        )

        self.workflow_tree.communicator_selected(communicator_view)
        self.system_state.entity_creator.model = (
            self.factory_registry.notification_listener_factories[0]
            .create_model()
        )
        self.system_state.add_new_entity()

        self.assertIsNotNone(self.system_state.entity_creator)
        self.assertEqual(
            2, len(communicator_view.notification_listener_views)
        )
        self.assertEqual(
            2, len(self.workflow.notification_listeners)
        )

    def test_delete_notification_listener(self):
        communicator_view = (self.workflow_tree.workflow_view
                             .communicator_view[0])
        self.assertEqual(
            1, len(communicator_view.notification_listener_views)
        )
        self.assertEqual(
            1, len(self.workflow.notification_listeners)
        )

        notification_listener_view = (communicator_view
                                      .notification_listener_views[0])
        self.workflow_tree.notification_listener_selected(
            notification_listener_view
        )
        self.system_state.remove_entity()

        self.assertEqual(
            0, len(communicator_view.notification_listener_views)
        )
        self.assertEqual(
            0, len(self.workflow.notification_listeners)
        )

    def test_error_messaging(self):

        self.assertIsNone(self.system_state.selected_view)
        self.assertIn("No Item Selected", self.workflow_tree.selected_error)

        self.system_state.selected_view = self.workflow_tree.workflow_view
        self.assertIn(
            "An input slot is not named", self.workflow_tree.selected_error
        )

        parameter_view = (self.workflow_tree.workflow_view
                          .mco_view[0].parameter_view)
        self.system_state.selected_view = parameter_view

        self.assertIn("No errors", self.workflow_tree.selected_error)

        data_source_view = (
            self.workflow_tree.workflow_view.process_view[0]
            .execution_layer_views[0].data_source_views[0]
        )
        data_source_view.model.output_slot_info[0].name = 'something'
        self.system_state.selected_view = data_source_view

        self.assertIn(
            "An output variable has an undefined name",
            self.workflow_tree.selected_error
        )

        self.assertIn(
            "A KPI is not named",
            self.workflow_tree.workflow_view.error_message
        )


class TestProcessElementNode(TestCase):

    def test_wfelement_node(self):

        wfelement_node = TreeNodeWithStatus()
        obj = mock.Mock()
        obj.valid = True
        self.assertEqual(wfelement_node.get_icon(obj, False),
                         'icons/valid.png')
        obj.valid = False
        self.assertEqual(wfelement_node.get_icon(obj, False),
                         'icons/invalid.png')
