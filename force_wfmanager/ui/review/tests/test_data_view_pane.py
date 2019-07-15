import unittest

from force_wfmanager.model.analysis_model import AnalysisModel
from force_wfmanager.ui.review.data_view_pane import DataViewPane
from force_wfmanager.ui.review.plot import Plot


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
        # plugin discovery. One default plot will be found as it's the only
        # one which is automatically populated.
        self.assertIn(Plot, self.pane.available_data_views)
        self.assertEqual(len(self.pane.available_data_views), 1)

    def test_data_view_descriptions(self):
        # the "change" button needs to be fired to populate the descriptions
        self.pane.change_view = True
        self.assertIn(
            "Plot with colormap (force_wfmanager.ui.review.plot.Plot)",
            self.pane.data_view_descriptions.values()
        )
