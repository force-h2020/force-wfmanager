import unittest
import warnings

from chaco.api import Plot as ChacoPlot
from chaco.api import ScatterPlot
from chaco.api import ColormappedScatterPlot
from chaco.abstract_colormap import AbstractColormap

from force_wfmanager.ui.review.base_plot import BasePlot
from force_wfmanager.ui.review.color_plot import ColorPlot
from traits.api import push_exception_handler, TraitError

from .plot_base_test_case import PlotBaseTestCase

push_exception_handler(reraise_exceptions=True)


class TestBasePlot(PlotBaseTestCase, unittest.TestCase):

    def setUp(self):
        super(TestBasePlot, self).setUp()
        self.plot = BasePlot(analysis_model=self.analysis_model)
        self.path = ("force_wfmanager.ui.review.base_plot."
                     + self.plot.__class__.__name__
                     + "._update_plot")


class TestPlot(PlotBaseTestCase, unittest.TestCase):

    def setUp(self):
        super(TestPlot, self).setUp()
        self.plot = ColorPlot(analysis_model=self.analysis_model)
        self.path = ("force_wfmanager.ui.review.color_plot."
                     + self.plot.__class__.__name__
                     + "._update_plot")

    def test_cmapped_plot(self):
        self.analysis_model.value_names = ('density', 'pressure', 'color')
        self.plot.color_plot = True
        self.plot.color_by = 'color'
        self.analysis_model.add_evaluation_step((1.010, 101325, 1))
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.assertEqual(self.plot.color_by, 'color')
            self.assertIsInstance(self.plot._plot, ChacoPlot)
            self.assertIsInstance(self.plot._axis, ColormappedScatterPlot)
            self.assertIsInstance(self.plot._axis.color_mapper,
                                  AbstractColormap)
            old_cmap = self.plot._axis.color_mapper
            self.plot.colormap = 'seismic'
            self.assertIsInstance(self.plot._axis.color_mapper,
                                  AbstractColormap)
            self.assertNotEqual(old_cmap, self.plot._axis.color_mapper)
            self.assertEqual(old_cmap.range,
                             self.plot._axis.color_mapper.range)

        with self.assertRaises(TraitError):
            self.plot.colormap = 'not_viridis'

        self.plot.colormap = 'viridis'
        self.plot.colormap = 'CoolWarm'

        self.plot.color_plot = False
        self.assertIsInstance(self.plot._axis, ScatterPlot)

    def test_ranges_are_kept(self):
        self.analysis_model.value_names = ('density', 'pressure', 'color')
        self.analysis_model.add_evaluation_step((1.010, 101325, 1))
        self.plot._set_plot_range(0.5, 2, 100000, 103000)
        self.plot.color_plot = True
        self.plot.color_by = 'color'
        self.assertEqual(self.plot._get_plot_range(), (0.5, 2, 100000, 103000))
        self.assertEqual(self.plot._plot.x_axis.title, "density")
        self.assertEqual(self.plot._plot.y_axis.title, "pressure")
