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

    def test_data_arrays(self):
        self.analysis_model.value_names = ['density', 'pressure']
        self.analysis_model.evaluation_steps = [
            (1.010, 101325),
            (1.100, 101423),
            (1.123, 102000),
            (1.156, 102123),
            (1.242, 102453),
        ]

        self.assertEqual(len(self.plot.data_arrays), 2)

        self.assertEqual(len(self.plot.data_arrays[0]), 5)
        self.assertEqual(len(self.plot.data_arrays[1]), 5)

        self.assertEqual(
            self.plot.data_arrays[0],
            [1.010, 1.100, 1.123, 1.156, 1.242]
        )

        self.assertEqual(
            self.plot.data_arrays[1],
            [101325, 101423, 102000, 102123, 102453]
        )

    def test_plot(self):
        self.analysis_model.value_names = ['density', 'pressure']
        self.analysis_model.evaluation_steps = [
            (1.010, 101325),
        ]

        self.assertIsInstance(self.plot.plot, ChacoPlot)
