import unittest

from force_wfmanager.central_pane.analysis_model import AnalysisModel


class AnalysisModelTest(unittest.TestCase):
    def setUp(self):
        self.analysis = AnalysisModel()

    def test_analysis_init(self):
        self.assertEqual(len(self.analysis.value_names), 0)
        self.assertEqual(len(self.analysis.evaluation_steps), 0)
        self.assertIsNone(self.analysis.selected_step_index)
