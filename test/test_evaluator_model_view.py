import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from envisage.plugin import Plugin

from force_bdss.core_plugins.dummy.csv_extractor.csv_extractor_data_source import CSVExtractorDataSource  # noqa
from force_bdss.core_plugins.dummy.csv_extractor.csv_extractor_factory import \
    CSVExtractorFactory

from force_wfmanager.left_side_pane.evaluator_model_view import \
    EvaluatorModelView


class EvaluatorModelViewTest(unittest.TestCase):
    def setUp(self):
        self.model = CSVExtractorFactory(mock.Mock(spec=Plugin)).create_model()

        self.evaluator_mv = EvaluatorModelView(model=self.model)

    def test_evaluator_model_view_init(self):
        self.assertEqual(self.evaluator_mv.label, "CSV Extractor")
        self.assertIsInstance(
            self.evaluator_mv._evaluator,
            CSVExtractorDataSource)
        self.assertEqual(len(self.evaluator_mv.output_slots_representation), 1)
        self.assertEqual(self.model.output_slot_names[0], '')

    def test_output_slot_update(self):
        self.evaluator_mv.output_slots_representation[0].name = 'test'
        self.assertEqual(self.model.output_slot_names[0], 'test')
