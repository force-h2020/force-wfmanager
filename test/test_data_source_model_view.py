import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from force_bdss.api import BaseDataSourceModel, BaseDataSourceFactory

from force_wfmanager.left_side_pane.data_source_model_view import \
    DataSourceModelView


class DataSourceModelViewTest(unittest.TestCase):
    def setUp(self):
        mock_model = mock.Mock(spec=BaseDataSourceModel)
        mock_model.input_slot_maps = []
        mock_model.output_slot_names = ["T1"]
        mock_model.factory = mock.Mock(spec=BaseDataSourceFactory)
        mock_model.factory.name = "baz"

        self.data_source_mv = DataSourceModelView(model=mock_model)

    def test_data_source_model_view_init(self):
        self.assertEqual(self.data_source_mv.label, "baz")
