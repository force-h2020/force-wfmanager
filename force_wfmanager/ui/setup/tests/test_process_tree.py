from force_bdss.api import ExecutionLayer
from force_wfmanager.ui.setup.tests.template_test_case import TestProcess
from force_wfmanager.ui.setup.process.process_view import (
    ProcessView
)
from force_wfmanager.ui.setup.process_tree import (
    ProcessTree
)
from force_wfmanager.ui.setup.system_state import SystemState


class TestProcessTreeModelView(TestProcess):

    def setUp(self):
        super(TestProcessTreeModelView, self).setUp()
        data_sources = [
            self.factory_registry.data_source_factories[2].create_model(),
            self.factory_registry.data_source_factories[3].create_model()
        ]
        execution_layer = ExecutionLayer(
            data_sources=data_sources
        )
        self.workflow.execution_layers.append(execution_layer)
        self.process_view = ProcessView(
            model=self.workflow,
            variable_names_registry=self.variable_names_registry,
        )
        self.system_state = SystemState()
        self.process_tree = ProcessTree(
            process_view=self.process_view,
            _factory_registry=self.factory_registry,
            system_state=self.system_state
        )

    def test_ui_initialization(self):
        print(self.workflow.execution_layers)
        self.assertEqual(
            len(self.process_tree.process_view.model.execution_layers), 2)
        self.assertEqual(
            len(self.process_tree.process_view.execution_layer_views), 2)

    def test_new_data_source(self):

        exec_layer = self.process_tree.process_view\
            .execution_layer_views[0]
        self.assertEqual(len(exec_layer.data_source_views), 2)
        self.assertEqual(
            len(self.process_tree.process_view.model\
                .execution_layers[0].data_sources), 2
        )

        self.process_tree.system_state.factory_instance(
            self.factory_registry.data_source_factories,
            self.process_tree.new_data_source,
            'ExecutionLayer',
            self.process_tree.delete_layer,
            exec_layer
        )

        self.process_tree.system_state.entity_creator.model = (
            self.factory_registry.data_source_factories[0].create_model()
        )
        self.process_tree.system_state.add_new_entity()

        self.assertEqual(len(exec_layer.data_source_views), 3)
        self.assertEqual(
            len(self.process_tree.process_view.model \
                .execution_layers[0].data_sources), 3
        )

    def test_new_execution_layer(self):
        self.assertEqual(
            len(self.process_tree.process_view.execution_layer_views)
            , 2)
        self.assertEqual(
            len(self.process_tree.process_view.model.execution_layers)
            , 2)

        self.process_tree.system_state.factory(
            None,
            self.process_tree.new_layer,
            'ExecutionLayer',
            self.process_tree.process_view
        )
        self.process_tree.system_state.add_new_entity()

        self.assertEqual(
            len(self.process_tree.process_view.execution_layer_views)
            , 3)
        self.assertEqual(
            len(self.process_tree.process_view.model.execution_layers)
            , 3)

    def test_delete_data_source(self):
        data_source = (
            self.process_tree.process_view.execution_layer_views[0]
                .data_source_views[0]
        )
        self.assertEqual(
            len(self.process_tree.process_view.execution_layer_views[0]
                .data_source_views),
            2)
        self.assertEqual(
            len(self.process_tree.process_view.model.execution_layers[0]
                .data_sources),
            2)

        self.process_tree.system_state.instance(
            self.process_tree.delete_data_source,
            data_source)
        self.process_tree.system_state.remove_entity()

        self.assertEqual(
            len(self.process_tree.process_view.execution_layer_views[0]
                .data_source_views),
            1)
        self.assertEqual(
            len(self.process_tree.process_view.model.execution_layers[0]
                .data_sources),
            1)

    def test_delete_execution_layer(self):
        first_execution_layer = (
            self.process_tree.process_view.execution_layer_views[0]
        )
        self.assertEqual(
            len(self.process_tree.process_view.execution_layer_views),
             2)
        self.assertEqual(
            len(self.process_tree.process_view.model.execution_layers)
            , 2)

        self.process_tree.system_state.factory_instance(
            self.factory_registry.data_source_factories,
            self.process_tree.new_data_source,
            'ExecutionLayer',
            self.process_tree.delete_layer,
            first_execution_layer
        )
        self.process_tree.system_state.remove_entity()

        self.assertEqual(
            len(self.process_tree.process_view.execution_layer_views)
            , 1)
        self.assertEqual(
            len(self.process_tree.process_view.model.execution_layers)
            , 1)

    def test_error_messaging(self):

        self.assertIsNone(self.process_tree.selected_view)
        self.assertIn("No Item Selected", self.process_tree.selected_error)
