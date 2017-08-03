import unittest

from force_wfmanager.central_pane.analysis import Analysis


class AnalysisTest(unittest.TestCase):
    def setUp(self):
        self.analysis = Analysis()

    def test_analysis_init(self):
        self.assertEqual(len(self.analysis.value_names), 0)
        self.assertEqual(len(self.analysis.evaluation_steps), 0)
        self.assertIsNone(self.analysis.selected_step_index)

        self.assertEqual(
            self.analysis.result_table.evaluation_steps,
            self.analysis.evaluation_steps
        )
        self.assertEqual(
            self.analysis.result_table.value_names,
            self.analysis.value_names
        )

    def test_evaluation_steps(self):
        self.analysis.evaluation_steps = [
            (2.3, 5.2, 'C0'),
            (23, 52, 'C02'),
        ]
        self.assertEqual(len(self.analysis.evaluation_steps), 2)
