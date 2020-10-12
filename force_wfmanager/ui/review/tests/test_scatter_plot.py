#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

import warnings

from chaco.api import Plot as ChacoPlot
from chaco.api import ScatterPlot as ChacoScatterPlot
from chaco.api import ColormappedScatterPlot
from chaco.abstract_colormap import AbstractColormap
from traits.api import push_exception_handler

from force_wfmanager.ui.review.scatter_plot import ScatterPlot

from .test_base_data_view import BasePlotTestCase

push_exception_handler(reraise_exceptions=True)


class TestScatterPlot(BasePlotTestCase):

    plot_cls = ScatterPlot

    def test_plot(self):
        self.analysis_model.header = ("density", "pressure")
        self.analysis_model.notify((1.010, 101325))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertIsInstance(self.plot._plot, ChacoPlot)
            self.assertIsInstance(self.plot._axis, ChacoScatterPlot)

    def test_cmapped_plot(self):
        self.analysis_model.header = ("density", "pressure", "color")
        self.analysis_model.notify((1.010, 101325, 1))
        self.check_update_is_requested_and_apply()
        self.plot.use_color_plot = True
        self.plot.color_by = "color"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertEqual(self.plot.color_by, "color")
            self.assertIsInstance(self.plot._plot, ChacoPlot)
            self.assertIsInstance(self.plot._axis, ColormappedScatterPlot)
            self.assertIsInstance(
                self.plot._axis.color_mapper, AbstractColormap
            )
            old_cmap = self.plot._axis.color_mapper
            self.plot.colormap = "seismic"
            self.assertIsInstance(
                self.plot._axis.color_mapper, AbstractColormap
            )
            self.assertNotEqual(old_cmap, self.plot._axis.color_mapper)
            self.assertEqual(
                old_cmap.range, self.plot._axis.color_mapper.range
            )

        self.plot.colormap = "viridis"
        self.plot.colormap = "CoolWarm"
        self.plot.use_color_plot = False
        self.assertIsInstance(self.plot._axis, ChacoScatterPlot)
