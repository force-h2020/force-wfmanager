#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

import unittest

from force_wfmanager.model.analysis_model import AnalysisModel
from force_wfmanager.ui.review.results_pane import ResultsPane


class TestResultsPane(unittest.TestCase):
    def setUp(self):
        self.model = AnalysisModel()
        self.pane = ResultsPane(analysis_model=self.model)

    def test_pane_init(self):
        self.assertEqual(len(self.pane.analysis_model.header), 0)
        self.assertEqual(len(self.pane.analysis_model.evaluation_steps), 0)
        self.assertIsNone(self.pane.analysis_model.selected_step_indices)

        self.assertEqual(
            self.pane.results_table.analysis_model.evaluation_steps,
            self.pane.analysis_model.evaluation_steps,
        )

        self.assertEqual(
            self.pane.results_table.analysis_model.header,
            self.pane.analysis_model.header,
        )

    def test_evaluation_steps_update(self):
        self.pane.analysis_model.header = ["x", "y", "z"]
        self.pane.analysis_model.notify((2.3, 5.2, "C0"))
        self.pane.analysis_model.notify((23, 52, "C02"))
        self.assertEqual(len(self.pane.analysis_model.evaluation_steps), 2)
        self.assertEqual(
            len(self.pane.results_table.analysis_model.evaluation_steps), 2
        )
