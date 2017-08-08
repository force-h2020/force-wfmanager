import unittest

from force_wfmanager.central_pane.analysis_model import AnalysisModel
from force_wfmanager.central_pane.result_table import ResultTable


class ResultTableTest(unittest.TestCase):
    def setUp(self):
        analysis_model = AnalysisModel(
            value_names=['x', 'y', 'compound'],
            evaluation_steps=[
                (2.1, 56, 'CO'),
                (1.23, 51.2, 'CO2')
            ])
        self.result_table = ResultTable(
            analysis_model=analysis_model
        )

    def test_columns(self):
        self.assertEqual(len(self.result_table.columns), 3)
        self.assertEqual(self.result_table.columns[2].label, 'compound')

    def test_value(self):
        column_2 = self.result_table.columns[2]
        row_1 = self.result_table.analysis_model.evaluation_steps[1]
        self.assertEqual(column_2.get_value(row_1), 'CO2')
