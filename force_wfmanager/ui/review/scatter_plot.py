#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.
""" This submodule implements the following :class:`BaseDataView` subclasses:

* :class:`Scatter` extends :class:`BasePlot` to allow for an
  optional colourmap to be applied to a third variable.

"""

from chaco.default_colormaps import color_map_name_dict
from chaco.api import Plot as ChacoPlot
from chaco.api import ScatterInspectorOverlay
from chaco.tools.api import BetterSelectingZoom as ZoomTool
from chaco.tools.api import PanTool, ScatterInspector
from enable.api import KeySpec
from traits.api import (
    Button,
    Bool,
    Dict,
    Enum,
    List,
    on_trait_change,
    Str,
    Property
)
from traitsui.api import EnumEditor, HGroup, Item, UItem, View

from .base_plot import BasePlot


class ScatterPlot(BasePlot):
    """Simple 2D scatter plot with optional colormap (see module doc)."""

    #: Short description for the UI selection
    description = "Scatter plot with colormap"

    # ------------------
    # Regular Attributes
    # ------------------

    #: Whether or not to include individually colored data points
    #: in displayed plot
    use_color_plot = Bool(False)

    #: Optional third parameter used to set colour of points
    color_by = Enum(values="displayable_value_names")

    #: Colour options button:
    color_options = Button("Color...")

    #: Available color maps provided by plotting backend
    _available_color_maps = Dict(color_map_name_dict)

    # --------------------
    # Dependent Attributes
    # --------------------

    #: Selectable color maps
    colormap = Enum(
        values="_available_color_map_names",
        depends_on="_available_color_map_names",
    )

    # ----------
    # Properties
    # ----------

    #: Available color maps names provided by plotting backend
    _available_color_map_names = Property(
        List(Str), depends_on='_available_color_maps')

    # ----
    # View
    # ----

    def _color_options_fired(self):
        """ Event handler for :attr:`color_options` button. """
        view = View(
            Item("use_color_plot"),
            Item("color_by", enabled_when="use_color_plot"),
            Item("colormap", enabled_when="use_color_plot"),
            kind="livemodal",
        )
        self.edit_traits(view=view)

    def _axis_hgroup_default(self):
        return HGroup(
            Item("x", editor=EnumEditor(name="displayable_value_names")),
            Item("y", editor=EnumEditor(name="displayable_value_names")),
            UItem("color_options"),
            Item("toggle_automatic_update", label="Axis auto update"),
        )

    # ----------
    # Properties
    # ----------

    def _get__available_color_map_names(self):
        return ["viridis"] + [
            cmap_name
            for cmap_name in self._available_color_maps.keys()
            if cmap_name != "viridis"
        ]

    # ---------
    # Listeners
    # ---------

    @on_trait_change("color_by")
    def _update_color_plot(self):
        if (
            self.x == ""
            or self.y == ""
            or self.color_by is None
            or self.analysis_model.is_empty
        ):
            self._plot_data.set_data("color_by", [])
            return

        self._plot_data.set_data(
            "color_by", self.analysis_model.column(self.color_by)
        )

    @on_trait_change("colormap")
    def _update_cmap(self):
        cmap = self._available_color_maps[self.colormap]
        if hasattr(self._axis, 'color_mapper'):
            _range = self._axis.color_mapper.range
            self._axis.color_mapper = cmap(_range)

    @on_trait_change("use_color_plot")
    def change_plot_style(self):
        ranges = self._get_plot_range()
        x_title = self._plot.x_axis.title
        y_title = self._plot.y_axis.title

        self._plot = ChacoPlot(self._plot_data)
        self.add_plots(self._plot)

        self._set_plot_range(*ranges)
        self._plot.x_axis.title = x_title
        self._plot.y_axis.title = y_title

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

    def add_plot_data(self, plot_data):
        plot_data.set_data("color_by", [])

    def update_data_view(self):
        self._update_color_plot()
