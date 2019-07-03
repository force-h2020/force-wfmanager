import unittest

from force_bdss.api import ExecutionLayer, Workflow
from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin

from force_wfmanager.ui.setup.process.process_model_view import ProcessModelView
from force_wfmanager.utils.variable_names_registry import \
    VariableNamesRegistry
from force_bdss.tests.probe_classes.data_source import (ProbeDataSourceFactory,
                                                        ProbeDataSourceModel)


class TestProcessModelView(unittest.TestCase):

    def setUp(self):
        workflow = Workflow()
        name_registry = VariableNamesRegistry(workflow)
        self.process_model_view = ProcessModelView(
            model=workflow,
            variable_names_registry=name_registry
        )
        self.plugin = ProbeExtensionPlugin()
        self.datasource_models = [ProbeDataSourceModel(
            factory=ProbeDataSourceFactory(plugin=self.plugin))
            for _ in range(2)]

    def test_add_execution_layer(self):
        self.assertEqual(
            len(self.process_model_view.execution_layer_model_views), 0)
        self.process_model_view.add_execution_layer(ExecutionLayer())
        self.assertEqual(
            len(self.process_model_view.model.execution_layers), 1)
        self.assertEqual(
            len(self.process_model_view.execution_layer_model_views), 1)
        self.assertEqual(
            self.process_model_view.execution_layer_model_views[0].model,
            self.process_model_view.model.execution_layers[0]
        )

    def test_remove_execution_layer(self):
        self.process_model_view.add_execution_layer(ExecutionLayer())
        layer = self.process_model_view.model.execution_layers[0]
        self.process_model_view.remove_execution_layer(layer)

        self.assertEqual(
            len(self.process_model_view.model.execution_layers), 0)
        self.assertEqual(
            len(self.process_model_view.execution_layer_model_views), 0)
