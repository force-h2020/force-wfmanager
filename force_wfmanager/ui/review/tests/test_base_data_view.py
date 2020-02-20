from unittest import TestCase
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from traits.testing.api import UnittestTools

from force_wfmanager.ui.review.base_data_view import BaseDataView
from force_wfmanager.model.analysis_model import AnalysisModel


class TestAnyPlot(GuiTestAssistant, TestCase, UnittestTools):
    def setUp(self):
        super().setUp()
        self.analysis_model = AnalysisModel()
        self.plot = BaseDataView(analysis_model=self.analysis_model)

    def test__update_data_arrays(self):
        self.assertEqual(0, len(self.plot.data_arrays))

        self.analysis_model.value_names = ("one", "two")
        self.assertEqual(0, len(self.analysis_model.evaluation_steps))
        self.plot._update_data_arrays()
        self.assertListEqual(self.plot.data_arrays, [[], []])

        self.analysis_model.add_evaluation_step((1, 2))
        self.analysis_model.add_evaluation_step((3, 4))

        self.plot._update_data_arrays()
        self.assertListEqual(
            self.plot.data_arrays[0],
            [
                self.analysis_model.evaluation_steps[0][0],
                self.analysis_model.evaluation_steps[1][0],
            ],
        )

        self.assertListEqual(
            self.plot.data_arrays[1],
            [
                self.analysis_model.evaluation_steps[0][1],
                self.analysis_model.evaluation_steps[1][1],
            ],
        )

        self.analysis_model.clear()
        self.assertEqual(0, len(self.analysis_model.value_names))
        self.assertEqual(0, len(self.analysis_model.evaluation_steps))

        self.plot._update_data_arrays()
        self.assertListEqual(self.plot.displayable_value_names, [])
        self.assertListEqual(self.plot.data_arrays, [])

        self.analysis_model.value_names = ("one", "two")
        self.plot._update_data_arrays()
        self.assertListEqual(self.plot.data_arrays, [[], []])
