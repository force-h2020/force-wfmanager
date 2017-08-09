import unittest

from chaco.api import Plot as ChacoPlot

from force_wfmanager.central_pane.analysis_model import AnalysisModel
from force_wfmanager.central_pane.plot import Plot


class PlotTest(unittest.TestCase):
    def setUp(self):
        self.analysis_model = AnalysisModel()
        self.plot = Plot(analysis_model=self.analysis_model)

    def test_init(self):
        self.assertEqual(len(self.analysis_model.value_names), 0)
        self.assertEqual(len(self.analysis_model.evaluation_steps), 0)
        self.assertEqual(len(self.plot.data_arrays), 0)
        self.assertIsNone(self.plot.plot)
        self.assertIsNone(self.plot.x)
        self.assertIsNone(self.plot.y)

    def test_init_data_arrays(self):
        self.analysis_model.value_names = ['density', 'pressure']
        self.assertEqual(self.plot.data_arrays, [[], []])

    def test_plot(self):
        self.analysis_model.value_names = ['density', 'pressure']
        self.analysis_model.evaluation_steps = [
            (1.010, 101325),
        ]

        self.assertIsInstance(self.plot.plot, ChacoPlot)

    def test_push_new_evaluation_steps(self):
        self.analysis_model.value_names = ['density', 'pressure']
        self.analysis_model.evaluation_steps = [
            (1.010, 101325),
            (1.100, 101423),
        ]

        self.assertEqual(len(self.plot.data_arrays), 2)

        first_data_array = self.plot.data_arrays[0]
        second_data_array = self.plot.data_arrays[1]

        self.assertEqual(first_data_array, [1.010, 1.100])
        self.assertEqual(second_data_array, [101325, 101423])

        # Append only one evaluation step
        self.analysis_model.evaluation_steps.append((1.123, 102000))

        self.assertEqual(first_data_array, [1.010, 1.100, 1.123])
        self.assertEqual(second_data_array, [101325, 101423, 102000])

        # Append two evaluation steps at the same time
        self.analysis_model.evaluation_steps.append((1.156, 102123))
        self.analysis_model.evaluation_steps.append((1.242, 102453))

        self.assertEqual(
            first_data_array, [1.010, 1.100, 1.123, 1.156, 1.242])
        self.assertEqual(
            second_data_array, [101325, 101423, 102000, 102123, 102453])

    def test_reinitialize_model(self):
        self.analysis_model.value_names = ['density', 'pressure']
        self.analysis_model.evaluation_steps = [
            (1.010, 101325),
            (1.100, 101423),
        ]

        self.assertEqual(len(self.plot.data_arrays), 2)

        first_data_array = self.plot.data_arrays[0]
        second_data_array = self.plot.data_arrays[1]

        self.assertEqual(first_data_array, [1.010, 1.100])
        self.assertEqual(second_data_array, [101325, 101423])

        self.analysis_model.evaluation_steps = []

        self.assertEqual(first_data_array, [])
        self.assertEqual(second_data_array, [])
