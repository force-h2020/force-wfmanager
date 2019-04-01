import unittest

from force_wfmanager.central_pane.analysis_model import AnalysisModel
from force_wfmanager.central_pane.graph_pane import GraphPane


class TestGraphPane(unittest.TestCase):
    def setUp(self):
        self.model = AnalysisModel()
        self.pane = GraphPane(self.model)

    def test_pane_init(self):
        self.assertEqual(len(self.pane.analysis_model.value_names), 0)
        self.assertEqual(len(self.pane.analysis_model.evaluation_steps), 0)
        self.assertIsNone(self.pane.analysis_model.selected_step_indices)

        self.assertEqual(
            self.pane.plot.analysis_model.evaluation_steps,
            self.pane.analysis_model.evaluation_steps
        )

        self.assertEqual(
            self.pane.plot.analysis_model.value_names,
            self.pane.analysis_model.value_names
        )

    def test_evaluation_steps_update(self):
        self.pane.analysis_model.value_names = ['x', 'y', 'z']
        self.pane.analysis_model.add_evaluation_step((2.3, 5.2, 'C0'))
        self.pane.analysis_model.add_evaluation_step((23, 52, 'C02'))
        self.assertEqual(len(self.pane.analysis_model.evaluation_steps), 2)
        self.assertEqual(
            len(self.pane.plot.analysis_model.evaluation_steps),
            2)
