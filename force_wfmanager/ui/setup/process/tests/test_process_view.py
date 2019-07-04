from force_wfmanager.ui.setup.tests.template_test_case import TestProcess
from force_wfmanager.ui.setup.process.process_view import (
    ProcessView
)


class TestProcessView(TestProcess):

    def setUp(self):
        super(TestProcessView, self).setUp()
        self.process_view = ProcessView(
            model=self.workflow,
            variable_names_registry=self.variable_names_registry,
        )

    def test_add_execution_layer(self):
        self.assertEqual(
            len(self.process_view.execution_layer_views), 1)
        self.process_view.add_execution_layer(self.execution_layer)
        self.assertEqual(
            len(self.process_view.model.execution_layers), 2)
        self.assertEqual(
            len(self.process_view.execution_layer_views), 2)
        self.assertEqual(
            self.process_view.execution_layer_views[1].model,
            self.process_view.model.execution_layers[1]
        )

    def test_remove_execution_layer(self):
        self.process_view.add_execution_layer(self.execution_layer)
        layer = self.process_view.model.execution_layers[1]
        self.process_view.remove_execution_layer(layer)

        self.assertEqual(
            len(self.process_view.model.execution_layers), 1)
        self.assertEqual(
            len(self.process_view.execution_layer_views), 1)
