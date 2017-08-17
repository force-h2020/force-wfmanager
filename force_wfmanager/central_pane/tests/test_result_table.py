import unittest

from force_wfmanager.central_pane.analysis_model import AnalysisModel
from force_wfmanager.central_pane.result_table import ResultTable


class ResultTableTest(unittest.TestCase):
    def setUp(self):
        self.analysis_model = AnalysisModel()

        self.analysis_model.value_names = ['x', 'y', 'compound']
        self.analysis_model.add_evaluation_step((2.1, 56, 'CO'))
        self.analysis_model.add_evaluation_step((1.23, 51.2, 'CO2'))
        self.result_table = ResultTable(
            analysis_model=self.analysis_model
        )

    def test_columns(self):
        self.assertEqual(len(self.result_table.columns), 3)
        self.assertEqual(self.result_table.columns[2].label, 'compound')

    def test_value(self):
        column_2 = self.result_table.columns[2]
        row_1 = self.analysis_model.evaluation_steps[1]
        self.assertEqual(column_2.get_value(row_1), 'CO2')

    def test_append_evaluation_steps(self):
        self.analysis_model.add_evaluation_step((1.5, 50, 'CO'))
        self.assertEqual(self.result_table.rows[2], (1.5, 50, 'CO'))

    def test_selection(self):
        # From table to the model
        self.assertIsNone(self.analysis_model.selected_step_index)

        self.result_table._selected_rows = [(2.1, 56, 'CO')]
        self.assertEqual(self.analysis_model.selected_step_index, 0)

        self.result_table._selected_rows = [(1.23, 51.2, 'CO2')]
        self.assertEqual(self.analysis_model.selected_step_index, 1)

        self.result_table._selected_rows = []
        self.assertIsNone(self.analysis_model.selected_step_index)

        # From model to the table
        self.analysis_model.selected_step_index = 1
        self.assertEqual(self.result_table._selected_rows,
                         [(1.23, 51.2, 'CO2')])

        self.analysis_model.selected_step_index = None
        self.assertEqual(self.result_table._selected_rows, [])
