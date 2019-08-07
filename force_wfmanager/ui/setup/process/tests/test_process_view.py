from force_bdss.api import ExecutionLayer

from force_wfmanager.ui.setup.process.process_view import (
    ProcessView
)
from force_wfmanager.ui.setup.tests.wfmanager_base_test_case import (
    WfManagerBaseTestCase
)


class TestProcessView(WfManagerBaseTestCase):

    def setUp(self):
        super(TestProcessView, self).setUp()
        self.process_view = ProcessView(
            model=self.workflow
        )

    def test__init__(self):
        self.assertEqual(
            1, len(self.process_view.execution_layer_views))
        self.assertEqual(
            'Layer 0', self.process_view.execution_layer_views[0].label)
        for data_source_view in \
                self.process_view.execution_layer_views[0].data_source_views:
            self.assertEqual(0, data_source_view.layer_index)

    def test_add_execution_layer(self):
        self.process_view.add_execution_layer(ExecutionLayer())
        self.assertEqual(
            2, len(self.process_view.model.execution_layers))
        self.assertEqual(
            2, len(self.process_view.execution_layer_views))
        self.assertEqual(
            self.process_view.execution_layer_views[1].model,
            self.process_view.model.execution_layers[1]
        )
        self.assertEqual(
            1, self.process_view.execution_layer_views[1].layer_index)
        self.assertEqual(
            'Layer 1', self.process_view.execution_layer_views[1].label)
        for data_source_view in \
                self.process_view.execution_layer_views[1].data_source_views:
            self.assertEqual(1, data_source_view.layer_index)

    def test_remove_execution_layer(self):
        self.process_view.add_execution_layer(self.execution_layer)
        layer = self.process_view.model.execution_layers[1]
        self.process_view.remove_execution_layer(layer)

        self.assertEqual(
            len(self.process_view.model.execution_layers), 1)
        self.assertEqual(
            len(self.process_view.execution_layer_views), 1)

    def test_remove_data_source(self):
        self.process_view.execution_layer_views[0].add_data_source(
            self.data_sources[0]
        )

        self.assertEqual(
            len(self.process_view.model.execution_layers[0]
                .data_sources), 3)
        self.assertEqual(
            len(self.process_view.execution_layer_views[0]
                .data_source_views), 3)

        self.process_view.remove_data_source(self.data_sources[0])

        self.assertEqual(
            len(self.process_view.model.execution_layers[0]
                .data_sources), 2)
        self.assertEqual(
            len(self.process_view.execution_layer_views[0]
                .data_source_views), 2)
