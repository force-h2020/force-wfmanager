import unittest

from force_wfmanager.model.analysis_model import AnalysisModel
from force_wfmanager.ui.review.data_view_pane import DataViewPane
from force_wfmanager.ui.review.plot import BasePlot, Plot


class TestDataViewPane(unittest.TestCase):
    def setUp(self):
        self.model = AnalysisModel()
        self.pane = DataViewPane(analysis_model=self.model)

    def test_pane_init(self):
        self.assertEqual(len(self.pane.analysis_model.value_names), 0)
        self.assertEqual(len(self.pane.analysis_model.evaluation_steps), 0)
        self.assertIsNone(self.pane.analysis_model.selected_step_indices)

        self.assertEqual(
            self.pane.data_view.analysis_model.evaluation_steps,
            self.pane.analysis_model.evaluation_steps
        )

        self.assertEqual(
            self.pane.data_view.analysis_model.value_names,
            self.pane.analysis_model.value_names
        )

    def test_evaluation_steps_update(self):
        self.pane.analysis_model.value_names = ['x', 'y', 'z']
        self.pane.analysis_model.add_evaluation_step((2.3, 5.2, 'C0'))
        self.pane.analysis_model.add_evaluation_step((23, 52, 'C02'))
        self.assertEqual(len(self.pane.analysis_model.evaluation_steps), 2)
        self.assertEqual(
            len(self.pane.data_view.analysis_model.evaluation_steps),
            2)

    def test_load_and_set_default_data_views(self):
        # This test class doesn't test the application, so there is no
        # plugin discovery. Two default plots will be found as they are
        # automatically populated.
        self.assertIn(Plot, self.pane.available_data_views)
        self.assertIn(BasePlot, self.pane.available_data_views)
        self.assertEqual(len(self.pane.available_data_views), 2)

    def test_change_data_view(self):
        # check the initial state
        self.assertEqual(
            self.pane.data_view_selection, BasePlot)
        self.assertIsInstance(
            self.pane.data_view, BasePlot)

        # then change data view
        self.pane.data_view_selection = Plot
        self.assertIsInstance(
            self.pane.data_view, Plot)

    def test_data_views_not_reinstantiated(self):
        # two data views are visited once
        initial = self.pane.data_view
        self.assertIsInstance(initial, BasePlot)
        self.pane.data_view_selection = Plot
        other = self.pane.data_view
        # they should be the same instance when visited again
        self.pane.data_view_selection = BasePlot
        self.assertTrue(self.pane.data_view is initial)
        self.pane.data_view_selection = Plot
        self.assertTrue(self.pane.data_view is other)

    def test_data_view_descriptions(self):
        # the "change" button needs to be fired to populate the descriptions
        self.pane.change_view = True
        self.assertIn(
            "Plot with colormap (force_wfmanager.ui.review.plot.Plot)",
            self.pane.data_view_descriptions.values()
        )
        self.assertIn(
            "Simple plot (force_wfmanager.ui.review.plot.BasePlot)",
            self.pane.data_view_descriptions.values()
        )
