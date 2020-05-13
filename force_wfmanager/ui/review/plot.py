""" This submodule implements the following :class:`BaseDataView` subclasses:

* :class:`BasePlot` provides a simple 2D scatter plot over the columns from
  the analysis model, with x and y selectable with a dropdown. It updates when
  new data is incoming, with a 1 second timer to avoid continuous updates.
  It is not selectable and is meant as a template for subclassing.
* :class:`Plot` extends :class:`BasePlot` to allow for an
  optional colourmap to be applied to a third variable.

"""
#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

import logging

from chaco.api import ArrayPlotData, ArrayDataSource, ScatterInspectorOverlay
from chaco.api import Plot as ChacoPlot
from chaco.api import BaseXYPlot, ColormappedScatterPlot
from chaco.default_colormaps import color_map_name_dict
from pyface.timer.api import CallbackTimer, do_later
from chaco.tools.api import PanTool, ScatterInspector, ZoomTool
from enable.api import Component, ComponentEditor
from enable.api import KeySpec
from traits.api import (
    Button,
    Bool,
    Dict,
    Enum,
    Instance,
    List,
    Property,
    on_trait_change,
    Str,
)
from traitsui.api import HGroup, Item, UItem, VGroup, View, EnumEditor

from .base_data_view import BaseDataView

log = logging.getLogger(__name__)


class BasePlot(BaseDataView):
    """Simple 2D scatter plot (see module-level doc)."""

    # -------------------
    # Required Attributes
    # -------------------

    #: Button to reset plot view. The button is active if :attr:`reset_enabled`
    #: is *True* and inactive if it is *False*.
    reset_plot = Button("Reset View")

    #: The plot abscissa axis name
    x = Str()

    #: The plot ordinate axis name
    y = Str()

    #: Optional third parameter used to set colour of points
    color_by = Enum(values="displayable_value_names")

    #: Optional title to display above the figure
    title = Str("Plot")

    #: Listens to: :attr:`analysis_model.selected_step_indices
    #: <force_wfmanager.central_pane.analysis_model.AnalysisModel.\
    #: selected_step_indices>`
    _plot_index_datasource = Instance(ArrayDataSource)

    # ----------
    # Properties
    # ----------

    #: Boolean indicating whether the plot view can be reset or not.
    reset_enabled = Property(Bool(), depends_on="_plot_data")

    # --------------------
    # Dependent Attributes
    # --------------------

    #: The 2D plot
    #: Listens to: :attr:`x`, :attr:`y`
    _plot = Instance(Component)

    _axis = Instance(BaseXYPlot)

    #: The plot data. This is the model of the actual Chaco plot.
    #: Listens to: :attr:`x`, :attr:`y`
    _plot_data = Instance(ArrayPlotData)

    #: Timer to check on required updates
    plot_updater = Instance(CallbackTimer)

    #: Schedule a refresh of plot data and axes. Set to True
    #: by default: the plot needs to be refreshed if the
    #: simulation was started from the 'Setup' pane.
    update_required = Bool(True)

    # ------------------
    # Regular Attributes
    # ------------------

    #: Short description for the UI selection
    description = "Simple plot"

    # ----
    # View
    # ----

    #: Controls the automatic axis update in the `_update_plot` call
    toggle_automatic_update = Bool(True)

    axis_hgroup = Instance(HGroup)

    def _axis_hgroup_default(self):
        return HGroup(
            Item("x", editor=EnumEditor(name="displayable_value_names")),
            Item("y", editor=EnumEditor(name="displayable_value_names")),
        )

    def default_traits_view(self):
        view = View(
            VGroup(
                self.axis_hgroup,
                UItem("_plot", editor=ComponentEditor()),
                VGroup(UItem("reset_plot", enabled_when="reset_enabled")),
            )
        )
        return view

    # --------------------
    # Defaults and getters
    # --------------------

    def _plot_updater_default(self):
        return CallbackTimer.timer(
            interval=1, callback=self._check_scheduled_updates
        )

    def __plot_default(self):
        plot = self.plot_scatter()
        self.plot_updater.start()
        # recenter_plot() requires self._plot to be defined
        do_later(self.recenter_plot)
        return plot

    def _get_scatter_inspector_overlay(self, scatter_plot):

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

        return inspector, overlay

    def plot_scatter(self):
        plot = ChacoPlot(self._plot_data)
        scatter_plot = plot.plot(
            ("x", "y"),
            type="scatter",
            name="Plot",
            marker="circle",
            index_sort="ascending",
            color="green",
            marker_size=4,
            bgcolor="white",
        )[0]

        plot.trait_set(title=self.title, padding=75, line_width=1)

        # Add pan and zoom tools
        scatter_plot.tools.append(PanTool(plot))
        scatter_plot.overlays.append(ZoomTool(plot))

        # Set the scatterplot's default selection marker invisible as it
        # lead to artifacts on axis when switching between plotted cols
        scatter_plot.trait_set(
            selection_color=(0, 0, 0, 0), selection_outline_color=(0, 0, 0, 0)
        )

        # Add the selection tool
        inspector, overlay = self._get_scatter_inspector_overlay(scatter_plot)
        scatter_plot.tools.append(inspector)
        scatter_plot.overlays.append(overlay)

        # Initialize plot datasource
        self._plot_index_datasource = scatter_plot.index
        self._axis = scatter_plot

        return plot

    def __plot_data_default(self):
        """ Default trait setter for _plot_data. Here it only uses an
        auxiliary method, but it can be overridden by inheriting classes
        to deal with more complex plot data.
        """
        return self._get_plot_data_default()

    def _get_plot_data_default(self):
        """ Creates empty plot data in three colums: x, y, color_by.
        """
        plot_data = ArrayPlotData()
        plot_data.set_data("x", [])
        plot_data.set_data("y", [])
        plot_data.set_data("color_by", [])
        return plot_data

    # ----------
    # Properties
    # ----------

    #: NOTE: appears to be updated very often (could do with caching?)
    def _get_reset_enabled(self):
        x_data = self._plot_data.get_data("x")
        if len(x_data) > 0:
            return True
        return False

    # ---------
    # Listeners
    # ---------

    # Response to analysis model changes

    @on_trait_change("displayable_value_names[]")
    def update_plot_axis_names(self):
        """ Update the plot axis to match the displayable_value_names."""
        if len(self.displayable_value_names) == 0:
            # If there are no displayable_value_names, set the plot view
            # to a default state.
            # This occurs when the analysis model is cleared, or no data
            # from the self.analysis_model is displayable.
            self._plot.x_axis.title = ""
            self._plot.y_axis.title = ""
            self.x = ""
            self.y = ""
        elif len(self.displayable_value_names) > 1:
            # If there is more than one displayable_value_names,
            # the x axis is set to the first displayable value name
            # (if the existing x axis is not displayable anymore),
            # the y axis is set to the second displayable value name
            # (if the existing y axis is not displayable anymore).
            if self.x not in self.displayable_value_names:
                self.x = self.displayable_value_names[0]
            if self.y not in self.displayable_value_names:
                self.y = self.displayable_value_names[1]
        else:
            # For a single displayable_value_names, both x and y
            # are set to the only available axis.
            self.y = self.displayable_value_names[0]
            self.x = self.displayable_value_names[0]

    @on_trait_change("analysis_model:evaluation_steps[]")
    def request_update(self):
        # Listens to the change in data points in the analysis model.
        # Enables the plot update at the next cycle.
        self.update_required = True

    @on_trait_change("is_active_view")
    def toggle_updater_with_visibility(self):
        """Start/stop the update if this data view is not being used. """
        if self.is_active_view:
            if not self.plot_updater.active:
                self.plot_updater.start()
            self.update_required = True
            self._check_scheduled_updates()
        else:
            if self.plot_updater.active:
                self.plot_updater.stop()
                log.warning("Stopped plot updater")

    @on_trait_change("x")
    def _update_plot_x_axis(self):
        """ Listens to the changes of the x-axis name. Updates the
        displayed data and resets the plot x axis."""
        self._update_plot_x_data()
        self.recenter_x_axis()

    def _update_plot_x_data(self):
        """ Update data points displayed by the x axis.
        Sets the x-`self._plot_data` to corresponding data in the
        `self.analysis_model`.
        This method is called by the `_update_plot` method during
        the callback update.
        This method is called when the `x` axis is changed.
        """
        if self.x == "" or self.analysis_model.is_empty:
            self._plot_data.set_data("x", [])
        else:
            self._plot.x_axis.title = self.x
            self._plot_data.set_data("x", self.analysis_model.column(self.x))

    def recenter_x_axis(self):
        """ Resets the bounds on the x-axis of the plot. If now x axis
        is specified, uses the default bounds (-1, 1). Otherwise, infers
        the bounds from the x-axis related data."""
        if self.x == "":
            bounds = (-1, 1)
        else:
            data = self._plot_data.get_data("x")
            bounds = self.calculate_axis_bounds(data)
        self._set_plot_x_range(*bounds)
        self._reset_zoomtool()
        return bounds

    def _set_plot_x_range(self, lower_bound, upper_bound):
        self._plot.range2d.x_range.low_setting = lower_bound
        self._plot.range2d.x_range.high_setting = upper_bound

    @on_trait_change("y")
    def _update_plot_y_axis(self):
        """ Listens to the changes of the y-axis name. Updates the
        displayed data and resets the plot y axis."""
        self._update_plot_y_data()
        self.recenter_y_axis()

    def _update_plot_y_data(self):
        """ Update data points displayed by the y axis.
        Sets the y-`self._plot_data` to corresponding data in the
        `self.analysis_model`.
        This method is called by the `_update_plot` method during
        the callback update.
        This method is called when the `y` axis is changed.
        """
        if self.y == "" or self.analysis_model.is_empty:
            self._plot_data.set_data("y", [])
        else:
            self._plot.y_axis.title = self.y
            self._plot_data.set_data("y", self.analysis_model.column(self.y))

    def recenter_y_axis(self):
        """ Resets the bounds on the x-axis of the plot. If now y axis
        is specified, uses the default bounds (-1, 1). Otherwise, infers
        the bounds from the y-axis related data."""
        if self.y == "":
            bounds = (-1, 1)
        else:
            data = self._plot_data.get_data("y")
            bounds = self.calculate_axis_bounds(data)

        self._set_plot_y_range(*bounds)
        self._reset_zoomtool()
        return bounds

    def _set_plot_y_range(self, lower_bound, upper_bound):
        self._plot.range2d.y_range.low_setting = lower_bound
        self._plot.range2d.y_range.high_setting = upper_bound

    @staticmethod
    def calculate_axis_bounds(data):
        set_length = len(set(data))
        if set_length > 1:
            axis_max = max(data) * 1.0
            axis_min = min(data)
            axis_spread = abs(axis_max - axis_min)
            axis_max = axis_max + 0.1 * axis_spread
            axis_min = axis_min - 0.1 * axis_spread
            bounds = (axis_min, axis_max)
        elif set_length == 1:
            bounds = (data[0] - 0.5, data[0] + 0.5)
        else:
            bounds = (-1, 1)
        return bounds

    def _reset_zoomtool(self):
        # Replace the old ZoomTool as retaining the same one can lead
        # to issues where the zoom out/in limit is not reset on
        # resizing the plot.
        for idx, overlay in enumerate(self._plot.overlays):
            if isinstance(overlay, ZoomTool):
                self._plot.overlays[idx] = ZoomTool(self._plot)

    def _update_plot(self):
        """Refresh the plot's axes and data. """
        if (
            self.x == ""
            or self.y == ""
            or self.color_by is None
            or self.analysis_model.is_empty
        ):
            self._plot_data.set_data("x", [])
            self._plot_data.set_data("y", [])
            self.recenter_plot()
            return

        self._update_plot_x_data()
        self._update_plot_y_data()
        if self.toggle_automatic_update:
            self.recenter_plot()

        self._plot_data.set_data(
            "color_by", self.analysis_model.column(self.color_by)
        )

    def _check_scheduled_updates(self):
        """ Update the plot if an update was required. This function is a
        callback for the _plot_updater timer.
        """
        if self.update_required:
            self._update_displayable_value_names()
            self._update_plot()
            self._reset_zoomtool()
            self.update_required = False

    def _reset_plot_fired(self):
        """ Event handler for :attr:`reset_plot`"""
        self.recenter_plot()

    def recenter_plot(self):
        """ Sets the size of the current plot to have some spacing
        between the largest/smallest value and the plot edge.
        """
        x_bounds = self.recenter_x_axis()
        y_bounds = self.recenter_y_axis()
        return (*x_bounds, *y_bounds)

    @on_trait_change("analysis_model:selected_step_indices")
    def update_selected_points(self):
        """ Updates the selected points in the plot according to the model """
        if self.analysis_model.selected_step_indices is None:
            self._plot_index_datasource.metadata["selections"] = []
        else:
            self._plot_index_datasource.metadata[
                "selections"
            ] = self.analysis_model.selected_step_indices

    @on_trait_change("_plot_index_datasource.metadata_changed")
    def update_model(self):
        """ Updates the model according to the selected point in the plot """
        selected_indices = self._plot_index_datasource.metadata.get(
            "selections", []
        )
        if len(selected_indices) == 0:
            self.analysis_model.selected_step_indices = None
        else:
            self.analysis_model.selected_step_indices = selected_indices

    def _set_plot_range(self, x_low, x_high, y_low, y_high):
        """ Helper method to set the size of the current _plot

        Parameters
        ----------
        x_low: Float
            Minimum value for x range of plot
        x_high: Float
            Maximum value for x range of plot
        y_low: Float
            Minimum value for y range of plot
        y_high: Float
            Maximum value for y range of plot
        """
        self._set_plot_x_range(x_low, x_high)
        self._set_plot_y_range(y_low, y_high)

    def _get_plot_range(self):
        """ Helper method to get the size of the current _plot

        Returns
        ----------
        x_low: Float
            Minimum value for x range of plot
        x_high: Float
            Maximum value for x range of plot
        y_low: Float
            Minimum value for y range of plot
        y_high: Float
            Maximum value for y range of plot
        """
        return (
            self._plot.range2d.x_range.low_setting,
            self._plot.range2d.x_range.high_setting,
            self._plot.range2d.y_range.low_setting,
            self._plot.range2d.y_range.high_setting,
        )


class Plot(BasePlot):
    """Simple 2D scatter plot with optional colormap (see module doc)."""

    # ------------------
    # Regular Attributes
    # ------------------

    #: Colour options button:
    color_options = Button("Color...")

    colormap = Enum(
        values="_available_colormaps_names",
        depends_on="_available_colormaps_names",
    )

    color_plot = Bool(False)

    #: Short description for the UI selection
    description = "Plot with colormap"

    # --------------------
    # Dependent Attributes
    # --------------------

    #: List of continuous chaco colormaps.
    __continuous_colormaps = Dict(color_map_name_dict)
    #: List of the names of continuous chaco colormaps.
    #: The default is set by the first entry of this list.
    __continuous_colormaps_names = ["viridis"] + [
        cmap_name
        for cmap_name in color_map_name_dict.keys()
        if cmap_name != "viridis"
    ]

    _available_colormaps = __continuous_colormaps
    _available_colormaps_names = List(
        __continuous_colormaps_names, depends_on="_available_colormaps"
    )

    def _axis_hgroup_default(self):
        return HGroup(
            Item("x", editor=EnumEditor(name="displayable_value_names")),
            Item("y", editor=EnumEditor(name="displayable_value_names")),
            UItem("color_options"),
            Item("toggle_automatic_update", label="Axis auto update"),
        )

    @on_trait_change("color_plot")
    def change_plot_style(self):
        ranges = self._get_plot_range()
        x_title = self._plot.x_axis.title
        y_title = self._plot.y_axis.title

        if self.color_plot:
            self._plot = self.plot_cmap_scatter()
        else:
            self._plot = self.plot_scatter()

        self._set_plot_range(*ranges)
        self._plot.x_axis.title = x_title
        self._plot.y_axis.title = y_title

    @on_trait_change("colormap")
    def _update_cmap(self):
        cmap = self._available_colormaps[self.colormap]
        if isinstance(self._axis, ColormappedScatterPlot):
            _range = self._axis.color_mapper.range
            self._axis.color_mapper = cmap(_range)

    def _color_options_fired(self):
        """ Event handler for :attr:`color_options` button. """
        view = View(
            Item("color_plot"),
            Item("color_by", enabled_when="color_plot"),
            Item("colormap", enabled_when="color_plot"),
            kind="livemodal",
        )
        self.edit_traits(view=view)

    def plot_cmap_scatter(self):
        plot = ChacoPlot(self._plot_data)

        cmap_scatter_plot = plot.plot(
            ("x", "y", "color_by"),
            type="cmap_scatter",
            name="Plot",
            marker="circle",
            fill_alpha=0.8,
            color_mapper=self._available_colormaps[self.colormap],
            marker_size=4,
            outline_color="black",
            index_sort="ascending",
            line_width=0,
            bgcolor="white",
        )[0]

        plot.trait_set(title="Plot", padding=75, line_width=1)

        # Add pan and zoom tools
        cmap_scatter_plot.tools.append(PanTool(plot))
        cmap_scatter_plot.overlays.append(ZoomTool(plot))

        # Add the selection tool
        inspector, overlay = self._get_scatter_inspector_overlay(
            cmap_scatter_plot
        )
        cmap_scatter_plot.tools.append(inspector)
        cmap_scatter_plot.overlays.append(overlay)

        self._plot_index_datasource = cmap_scatter_plot.index
        self._axis = cmap_scatter_plot

        return plot

    # Response to UI changes

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
