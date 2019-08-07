from force_wfmanager.ui.setup.process.execution_layer_view import (
    ExecutionLayerView
)
from force_wfmanager.ui.setup.tests.wfmanager_base_test_case import (
    WfManagerBaseTestCase
)


class TestExecutionLayerView(WfManagerBaseTestCase):

    def setUp(self):
        super(TestExecutionLayerView, self).setUp()
        self.execution_layer_view = ExecutionLayerView(
            layer_index=1,
            model=self.execution_layer
        )

    def test_init_with_data_sources(self):
        self.assertEqual(2, len(self.data_sources))
        self.assertEqual(2, len(self.execution_layer.data_sources))
        self.assertEqual(
            2, len(self.workflow.execution_layers[0].data_sources)
        )
        self.assertEqual(
            2, len(self.execution_layer_view.data_source_views)
        )
        for data_source_view in \
                self.execution_layer_view.data_source_views:
            self.assertEqual(1, data_source_view.layer_index)

    def test_add_data_source(self):
        factory = self.factory_registry.data_source_factories[1]
        model = factory.create_model()

        self.assertEqual(2, len(self.execution_layer.data_sources))
        self.assertEqual(
            2,
            len(self.execution_layer_view.data_source_views)
        )

        self.execution_layer_view.add_data_source(model)
        self.assertEqual(3, len(self.execution_layer.data_sources))
        self.assertEqual(
            3,
            len(self.execution_layer_view.data_source_views)
        )

    def test_remove_data_source(self):
        self.execution_layer_view.add_data_source(self.data_sources[0])
        self.assertEqual(3, len(self.execution_layer.data_sources))

        self.execution_layer_view.remove_data_source(self.data_sources[0])
        self.assertEqual(2, len(self.execution_layer.data_sources))
        self.assertEqual(
            2,
            len(self.execution_layer_view.data_source_views)
        )
