#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.
""" This submodule implements the following :class:`BaseDataView` subclasses:

* :class:`ScatterPlot` extends :class:`BasePlot` to display data as
    a 2D scatter plot.

"""

from chaco.api import ScatterInspectorOverlay
from chaco.tools.api import BetterSelectingZoom as ZoomTool
from chaco.tools.api import PanTool, ScatterInspector
from enable.api import KeySpec

from .base_plot import BasePlot


class ScatterPlot(BasePlot):
    """Simple 2D scatter plot with optional colormap (see module doc)."""

    #: Short description for the UI selection
    description = "Scatter plot with colormap"

    def _add_plot_tools(self, plot):
        """Add pan and zoom tools"""
        plot.tools.append(PanTool(plot))
        plot.overlays.append(ZoomTool(plot))

    def _add_scatter_inspector_overlay(self, scatter_plot):

        inspector = ScatterInspector(
            scatter_plot,
            threshold=10,
            multiselect_modifier=KeySpec(None, "shift"),
            selection_mode="multi",
        )

        overlay = ScatterInspectorOverlay(
            scatter_plot,
            hover_color=(0, 0, 1, 1),
            hover_marker_size=6,
            selection_marker_size=20,
            selection_color=(0, 0, 1, 0.5),
            selection_outline_color=(0, 0, 0, 0.8),
            selection_line_width=3,
        )

        scatter_plot.tools.append(inspector)
        scatter_plot.overlays.append(overlay)

    def plot_scatter(self, plot):
        if self.use_color_plot:
            args = (('x', 'y', 'color_by'),)
            kwargs = {
                "type": "cmap_scatter",
                "fill_alpha": 0.8,
                "color_mapper": self._available_color_maps[self.colormap],
                "outline_color": "black",
                "line_width": 0,
            }
        else:
            args = (('x', 'y'),)
            kwargs = {
                "type": "scatter",
                "color": "green",
            }

        scatter_plot = plot.plot(
            *args,
            **kwargs,
            name="Plot",
            marker="circle",
            index_sort="ascending",
            marker_size=4,
            bgcolor="white",
        )[0]

        plot.trait_set(title=self.title, padding=75, line_width=1)

        # Add pan and zoom tools
        self._add_plot_tools(scatter_plot)

        # Add the selection tool
        self._add_scatter_inspector_overlay(scatter_plot)

        # Set the scatterplot's default selection marker invisible as it
        # lead to artifacts on axis when switching between plotted cols
        scatter_plot.trait_set(
            selection_color=(0, 0, 0, 0),
            selection_outline_color=(0, 0, 0, 0)
        )

        # Initialize plot datasource
        self._axis = scatter_plot

        return plot

    def add_plots(self, plot):
        self.plot_scatter(plot)
