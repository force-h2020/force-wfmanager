from unittest import mock, TestCase
import warnings

from chaco.api import Plot as ChacoPlot
from chaco.api import BaseXYPlot
from chaco.api import ColormappedScatterPlot
from chaco.abstract_colormap import AbstractColormap
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant

from force_wfmanager.ui.review.base_plot import BasePlot
from force_wfmanager.ui.review.color_plot import ColorPlot
from traits.api import push_exception_handler, TraitError

from .plot_base_test_case import PlotBaseTestCase

push_exception_handler(reraise_exceptions=True)

COLOR_PLOT_EDIT_TRAITS_PATH = (
    "force_wfmanager.ui.review.color_plot.ColorPlot.edit_traits"
)


class TestBasePlot(PlotBaseTestCase, TestCase):

    def setUp(self):
        super(TestBasePlot, self).setUp()
        self.plot = BasePlot(analysis_model=self.analysis_model)
        self.path = ("force_wfmanager.ui.review.base_plot."
                     + self.plot.__class__.__name__
                     + "._update_plot")


class TestColorPlot(PlotBaseTestCase, TestCase, GuiTestAssistant):

    def setUp(self):
        super(TestColorPlot, self).setUp()
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
        self.assertIsInstance(self.plot._axis, BaseXYPlot)

    def test_ranges_are_kept(self):
        self.analysis_model.value_names = ('density', 'pressure', 'color')
        self.analysis_model.add_evaluation_step((1.010, 101325, 1))
        self.plot._set_plot_range(0.5, 2, 100000, 103000)
        self.plot.color_plot = True
        self.plot.color_by = 'color'
        self.assertEqual(self.plot._get_plot_range(), (0.5, 2, 100000, 103000))
        self.assertEqual(self.plot._plot.x_axis.title, "density")
        self.assertEqual(self.plot._plot.y_axis.title, "pressure")

    def test__color_options_fired(self):
        with mock.patch(COLOR_PLOT_EDIT_TRAITS_PATH) as mock_edit_traits:
            self.plot.color_options = True
            mock_edit_traits.assert_called()
