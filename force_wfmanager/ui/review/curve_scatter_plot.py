#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

import logging

import numpy as np
from scipy import interpolate

from chaco.api import BaseXYPlot
from traits.api import Instance, on_trait_change, Str, Bool
from traitsui.api import (
    HGroup, Item, UItem, VGroup, UReadonly, EnumEditor)

from force_wfmanager.ui.review.plot import Plot

log = logging.getLogger(__name__)

_ERROR = 'Unable to interpolate curve through data points'


class CurveScatterPlot(Plot):

    #: Short description for the UI selection
    description = "Scatter plot with curve overlay"

    #: Toggle to determine whether to overlay curve in the display
    toggle_display_curve = Bool()

    _curve_axis = Instance(BaseXYPlot)

    #: Whether the curve interpolation is successful or not with the
    #: displayed data
    _curve_status = Bool()

    #: Error message to display
    _curve_error = Str()

    def _axis_hgroup_default(self):
        return HGroup(
            Item("x", editor=EnumEditor(name="displayable_value_names")),
            Item("y", editor=EnumEditor(name="displayable_value_names")),
            UItem("color_options"),
            VGroup(
                Item("toggle_automatic_update", label="Axis auto update"),
                Item("toggle_display_curve", label="Display curve"),
                UReadonly("_curve_error", visible_when="not _curve_status")
            )
        )

    def _get_plot_data_default(self):
        """Extends plot data objects to add a dimension for the curve"""
        plot_data = super(CurveScatterPlot, self)._get_plot_data_default()
        plot_data.set_data("x_curve", [])
        plot_data.set_data("y_curve", [])
        return plot_data

    @on_trait_change("toggle_display_curve")
    def _update_curve_plot(self):
        """Updates curve line plot. Will attempt to interpolate a curve through
        the 2D data, and flag an error to display in the UI if fails.
        """

        if (
                self.x == ""
                or self.y == ""
                or self.analysis_model.is_empty
                or not self.toggle_display_curve
        ):
            self._plot_data.set_data("x_curve", [])
            self._plot_data.set_data("y_curve", [])
            self._curve_status = True
            return

        x = self._plot_data.get_data("x")
        y = self._plot_data.get_data("y")

        # Attempt to fit curve, reset the curves and display an error
        # if this fails
        try:
            f = interpolate.interp1d(x, y)
            x_curve = np.linspace(min(x), max(x), 20)
            y_curve = f(x_curve)

            self._plot_data.set_data("x_curve", x_curve)
            self._plot_data.set_data("y_curve", y_curve)
            self._curve_status = True
        except (TypeError, ValueError):
            self._plot_data.set_data("x_curve", [])
            self._plot_data.set_data("y_curve", [])
            self._curve_status = False

    def _add_curve(self, plot):
        """Adds a curve line plot to the ChacoPlot"""
        curve_plot = plot.plot(
            ("x_curve", "y_curve"),
            type="line",
            color="red"
        )[0]
        self._curve_axis = curve_plot

    def _update_plot(self):
        """Overloads the parent class method to update the curve plot"""
        super(CurveScatterPlot, self)._update_plot()
        self._update_curve_plot()

    @on_trait_change("x")
    def _update_plot_x_axis(self):
        """Overload the parent class method to update the curve plot"""
        super(CurveScatterPlot, self)._update_plot_x_axis()
        self._update_curve_plot()

    @on_trait_change("y")
    def _update_plot_y_axis(self):
        """Overload the parent class method to update the curve plot"""
        super(CurveScatterPlot, self)._update_plot_y_axis()
        self._update_curve_plot()

    def plot_scatter(self):
        """Overload the parent class method to add the curve plot"""
        plot = super(CurveScatterPlot, self).plot_scatter()
        self._add_curve(plot)
        return plot
