import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from force_bdss.api import BaseDataSourceModel, BaseDataSourceFactory

from force_wfmanager.left_side_pane.data_source_model_view import \
    DataSourceModelView


class TestKPICalculatorModelViewTest(unittest.TestCase):
    def setUp(self):
        mock_model = mock.Mock(spec=BaseDataSourceModel)
        mock_model.input_slot_maps = []
        mock_model.output_slot_names = ["T1"]
        mock_model.factory = mock.Mock(spec=BaseDataSourceFactory)
        mock_model.factory.name = "baz"

        self.data_source_mv = DataSourceModelView(model=mock_model)

    def test_data_source_model_view_init(self):
        self.assertEqual(self.data_source_mv.label, "baz")
        self.assertEqual(len(self.data_source_mv.input_slot_maps), 0)
        self.assertEqual(len(self.data_source_mv.output_slot_names), 1)

    def test_data_source_model_view_update(self):
        self.data_source_mv.model.input_slot_maps.append({'name': 'P1'})

        self.assertEqual(len(self.data_source_mv.input_slot_maps), 1)

        self.data_source_mv.model.output_slot_names.append("P2")

        self.assertEqual(len(self.data_source_mv.output_slot_names), 2)
