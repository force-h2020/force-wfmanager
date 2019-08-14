from force_wfmanager.ui.setup.process.data_source_view import (
    DataSourceView
)
from force_wfmanager.ui.setup.graph_display.process_graph_objects import (
    DataSourceBox
)
from force_wfmanager.ui.setup.tests.wfmanager_base_test_case import \
    WfManagerBaseTestCase


class TestDataSourceBox(WfManagerBaseTestCase):

    def setUp(self):
        super(TestDataSourceBox, self).setUp()
        self.data_source_view = DataSourceView(
            model=self.model_1
        )

        self.data_source_box = DataSourceBox(
            data_source_view=self.data_source_view
        )

    def test___init__(self):

        self.assertEqual(
            self.data_source_view,
            self.data_source_box.data_source_view
        )
        self.assertEqual(
            self.model_1,
            self.data_source_box.data_source_view.model
        )

        self.assertEqual(
            1, len(self.data_source_box.inputs)
        )
        self.assertEqual(
            2, len(self.data_source_box.outputs)
        )
        self.assertEqual(
            'test_data_source', self.data_source_box.text
        )
        self.assertEqual(
            'P1', self.data_source_box.inputs[0].model.name
        )


class TestExecutionLayerBox(WfManagerBaseTestCase):

    def setUp(self):
        super(TestExecutionLayerBox, self).setUp()

    def test___init__(self):
        pass
