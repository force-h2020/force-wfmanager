import unittest

from force_wfmanager.model.analysis_model import AnalysisModel
from force_wfmanager.ui.review.results_table import ResultsTable


class TestResultsTable(unittest.TestCase):
    def setUp(self):
        self.analysis_model = AnalysisModel()

        self.analysis_model.header = ["x", "y", "compound"]
        self.analysis_model.notify((2.1, 56, "CO"))
        self.analysis_model.notify((1.23, 51.2, "CO2"))
        self.results_table = ResultsTable(analysis_model=self.analysis_model)

    def test_columns(self):
        self.assertEqual(len(self.results_table.columns), 3)
        self.assertEqual(self.results_table.columns[2].label, "compound")

    def test_value(self):
        column_2 = self.results_table.columns[2]
        row_1 = self.analysis_model.evaluation_steps[1]
        self.assertEqual(column_2.get_value(row_1), "CO2")

    def test_append_evaluation_steps(self):
        self.analysis_model.notify((1.5, 50, "CO"))
        self.assertEqual(self.results_table.rows[2], (1.5, 50, "CO"))

    def test_selection(self):
        # From table to the model
        self.assertIsNone(self.analysis_model.selected_step_indices)

        self.results_table._selected_rows = [(2.1, 56, "CO")]
        self.assertEqual(self.analysis_model.selected_step_indices, [0])

        self.results_table._selected_rows = [(1.23, 51.2, "CO2")]
        self.assertEqual(self.analysis_model.selected_step_indices, [1])

        self.results_table._selected_rows = []
        self.assertIsNone(self.analysis_model.selected_step_indices)

        # From model to the table
        self.analysis_model.selected_step_indices = [1]
        self.assertEqual(
            self.results_table._selected_rows, [(1.23, 51.2, "CO2")]
        )

        self.analysis_model.selected_step_indices = [0, 1]
        self.assertEqual(
            self.results_table._selected_rows,
            [(2.1, 56, "CO"), (1.23, 51.2, "CO2")],
        )

        self.analysis_model.selected_step_indices = None
        self.assertEqual(self.results_table._selected_rows, [])
