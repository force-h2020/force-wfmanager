import unittest

from force_wfmanager.central_pane.analysis import Analysis


class AnalysisTest(unittest.TestCase):
    def setUp(self):
        self.analysis = Analysis()

    def test_analysis_init(self):
        self.assertEqual(len(self.analysis.value_names), 0)
        self.assertEqual(len(self.analysis.evaluation_steps), 0)

    def test_evaluation_steps(self):
        self.analysis.evaluation_steps = [
            [2.3, 5.2, 'pressure'],
            [23, 52, 'temperature'],
        ]
        self.assertEqual(len(self.analysis.evaluation_steps), 2)
