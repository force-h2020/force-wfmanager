import unittest

from force_bdss.api import (Workflow, ExecutionLayer, OutputSlotInfo,
    InputSlotInfo
)
from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin

from force_bdss.tests.probe_classes.data_source import (ProbeDataSourceFactory,
                                                        ProbeDataSourceModel)
from force_wfmanager.ui.setup.process.execution_layer_model_view import (
    ExecutionLayerModelView
)
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry)


class TestExecutionLayerModelView(unittest.TestCase):

    def setUp(self):
        self.plugin = ProbeExtensionPlugin()
        self.datasource_models = [ProbeDataSourceModel(
            factory=ProbeDataSourceFactory(plugin=self.plugin))
            for _ in range(2)]
        self.datasource_models[0].output_slot_info \
            = [OutputSlotInfo(name='outputA')]
        self.datasource_models[1].output_slot_info \
            = [OutputSlotInfo(name='outputB')]

        self.execution_layer = ExecutionLayer()
        self.workflow = Workflow(
            execution_layers = [self.execution_layer]
        )
        self.name_registry = VariableNamesRegistry(self.workflow)

        self.execution_layer_model_view = ExecutionLayerModelView(
            model=self.execution_layer,
            variable_names_registry=self.name_registry
        )

    def test_init_with_data_sources(self):
        execution_layer = ExecutionLayer(
            data_sources=self.datasource_models
        )
        workflow = Workflow(
            execution_layers=[execution_layer]
        )
        name_registry = VariableNamesRegistry(workflow)

        execution_layer_model_view = ExecutionLayerModelView(
            model=execution_layer,
            variable_names_registry=name_registry
        )

        self.assertEqual(
            len(execution_layer.data_sources), 2)
        print(name_registry.available_variables)
        self.assertEqual(
            len(execution_layer_model_view.data_source_model_views), 2)

    def test_add_data_source(self):
        self.assertEqual(
            len(self.execution_layer.data_sources),
            0)
        self.assertEqual(
            len(self.execution_layer_model_view.data_source_model_views),
            0)
        self.execution_layer_model_view.add_data_source(self.datasource_models[0])
        self.assertEqual(
            len(self.execution_layer.data_sources),
            1)
        self.assertEqual(
            len(self.execution_layer_model_view.data_source_model_views),
            1)

    def test_remove_data_source(self):
        self.execution_layer_model_view.add_data_source(self.datasource_models[0])
        self.assertEqual(
            len(self.execution_layer.data_sources),
            1)

        self.execution_layer_model_view.remove_data_source(self.datasource_models[0])
        self.assertEqual(
            len(self.execution_layer.data_sources),
            0)
        self.assertEqual(
            len(self.execution_layer_model_view.data_source_model_views),
            0)