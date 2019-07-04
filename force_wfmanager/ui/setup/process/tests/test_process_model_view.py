from .template_test_case import TestProcess
from force_wfmanager.ui.setup.process.process_model_view import (
    ProcessModelView
)


class TestProcessModelView(TestProcess):

    def setUp(self):
        super(TestProcessModelView, self).setUp()
        self.process_model_view = ProcessModelView(
            model=self.workflow,
            variable_names_registry=self.variable_names_registry,
        )

    def test_add_execution_layer(self):
        self.assertEqual(
            len(self.process_model_view.execution_layer_model_views), 1)
        self.process_model_view.add_execution_layer(self.execution_layer)
        self.assertEqual(
            len(self.process_model_view.model.execution_layers), 2)
        self.assertEqual(
            len(self.process_model_view.execution_layer_model_views), 2)
        self.assertEqual(
            self.process_model_view.execution_layer_model_views[1].model,
            self.process_model_view.model.execution_layers[1]
        )

    def test_remove_execution_layer(self):
        self.process_model_view.add_execution_layer(self.execution_layer)
        layer = self.process_model_view.model.execution_layers[1]
        self.process_model_view.remove_execution_layer(layer)

        self.assertEqual(
            len(self.process_model_view.model.execution_layers), 1)
        self.assertEqual(
            len(self.process_model_view.execution_layer_model_views), 1)
