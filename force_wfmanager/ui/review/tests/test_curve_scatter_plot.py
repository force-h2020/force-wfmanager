#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

from unittest import TestCase, mock

from chaco.api import ArrayPlotData
from chaco.api import Plot as ChacoPlot

from force_wfmanager.model.analysis_model import AnalysisModel
from force_wfmanager.ui.ui_utils import item_info_from_group
from force_wfmanager.ui.review.curve_scatter_plot import CurveScatterPlot


class TestCurveScatterPlot(TestCase):

    def setUp(self):
        self.analysis_model = AnalysisModel(
            header=['parameter_1', 'parameter_2',
                    'salt', 'kpi_1'],
            _evaluation_steps=[('A', 1.45, 0.5, 10),
                               ('A', 5.11, 1.0, 12),
                               ('B', 4.999, 1.1, 17),
                               ('B', 4.998, 2.0, 22)]
        )
        self.plot = CurveScatterPlot(
            analysis_model=self.analysis_model
        )

    def test_init(self):
        self.assertEqual("", self.plot.x)
        self.assertEqual("", self.plot.y)
        self.plot._update_plot()
        self.assertListEqual(
            [], self.plot._plot_data.get_data("x_curve").tolist())
        self.assertListEqual(
            [], self.plot._plot_data.get_data("y_curve").tolist())
        self.assertTrue(self.plot.plot_updater.active)
        self.assertTrue(self.plot.toggle_automatic_update)

    def test_axis_hgroup_default(self):
        self.assertListEqual(
            ['x', 'y', 'color_options', 'toggle_automatic_update',
             'toggle_display_curve', '_curve_error'],
            item_info_from_group(self.plot.axis_hgroup.content))

    def test_add_curve(self):
        plot_data = ArrayPlotData()
        plot_data.set_data("x_curve", [])
        plot_data.set_data("y_curve", [])
        plot = ChacoPlot(plot_data)

        self.plot._add_curve(plot)
        self.assertEqual(1, len(self.plot._sub_axes))
        self.assertIn('curve_plot', self.plot._sub_axes)

    def test_initialize_chaco_plots(self):
        self.assertDictEqual({}, self.plot._sub_axes)
        # Trigger the lazy default loader
        self.plot._plot = self.plot._plot
        self.assertEqual(1, len(self.plot._sub_axes))
        self.assertIn('curve_plot', self.plot._sub_axes)

    def test_plot_data_default(self):
        self.assertIn('x_curve', self.plot._plot_data.arrays)
        self.assertIn('y_curve', self.plot._plot_data.arrays)

    def test_update_curve_plot(self):
        self.assertFalse(self.plot.toggle_display_curve)
        self.plot._update_curve_plot()
        self.assertTrue(self.plot._curve_status)
        self.assertEqual(
            0, len(self.plot._plot_data.get_data("x_curve")))
        self.assertEqual(
            0, len(self.plot._plot_data.get_data("y_curve")))

        self.plot.x = 'parameter_2'
        self.plot.y = 'kpi_1'

        self.plot.toggle_display_curve = True
        self.assertEqual(
            20, len(self.plot._plot_data.get_data("x_curve")))
        self.assertEqual(
            20, len(self.plot._plot_data.get_data("y_curve")))
        self.assertTrue(self.plot._curve_status)

        self.plot.x = ""
        self.plot._update_curve_plot()
        self.assertEqual(
            0, len(self.plot._plot_data.get_data("x_curve")))
        self.assertEqual(
            0, len(self.plot._plot_data.get_data("y_curve")))

        def raise_error(*args, **kwargs):
            raise ValueError

        self.plot.x = "parameter_2"
        with mock.patch('scipy.interpolate.interp1d',
                        side_effect=raise_error):
            self.plot._update_curve_plot()
            self.assertEqual(
                0, len(self.plot._plot_data.get_data("x_curve")))
            self.assertEqual(
                0, len(self.plot._plot_data.get_data("y_curve")))
            self.assertFalse(self.plot._curve_status)
