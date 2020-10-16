""" This submodule implements the following :class:`BaseDataView` subclasses:

* :class:`BasePlot` provides a simple 2D plot over the columns from
  the analysis model, with x and y selectable from a dropdown. It updates when
  new data is incoming, with a 1 second timer to avoid continuous updates.
  It is not selectable and is meant as a template for subclassing.

"""
#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

import logging

from chaco.api import Plot as ChacoPlot
from chaco.api import ArrayPlotData, BaseXYPlot
from chaco.tools.api import BetterSelectingZoom as ZoomTool
from enable.api import Component, ComponentEditor
from pyface.timer.api import do_later
from traits.api import (
    Button,
    Bool,
    Instance,
    on_trait_change,
    Str,
    Dict,
    Property
)
from traitsui.api import EnumEditor, HGroup, VGroup, Item, UItem, View

from .base_data_view import BaseDataView

log = logging.getLogger(__name__)


class BasePlot(BaseDataView):
    """Base class for 2D Chaco plot with optional color view. Expected to be
    expanded upon when handling more complex data sets (see module-level doc).
    """

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

    #: Optional title to display above the figure
    title = Str("Plot")

    #: Listens to: :attr:`analysis_model.selected_step_indices
    #: <force_wfmanager.central_pane.analysis_model.AnalysisModel.\
    #: selected_step_indices>`
    _axis = Instance(BaseXYPlot)

    #: Container for referencing additional axes that are not hooked
    #: up to the data table
    _sub_axes = Dict(Str, BaseXYPlot)

    # --------------------
    # Dependent Attributes
    # --------------------

    #: Reference to the Chaco component to be displayed in the TraitsUI view
    _component = Instance(Component)

    #: The Chaco Component object representing the plot to be displayed
    #: Listens to: :attr:`x`, :attr:`y`
    _plot = Instance(ChacoPlot)

    #: The plot data. This is the model of the actual Chaco plot.
    #: Listens to: :attr:`x`, :attr:`y`
    _plot_data = Instance(ArrayPlotData)

    # ----------
    # Properties
    # ----------

    #: Boolean indicating whether the plot view can be reset or not.
    reset_enabled = Property(Bool(), depends_on="_plot_data")

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
            Item("toggle_automatic_update", label="Axis auto update"),
        )

    def default_traits_view(self):
        view = View(
            VGroup(
                self.axis_hgroup,
                UItem("_component", editor=ComponentEditor()),
                VGroup(UItem("reset_plot", enabled_when="reset_enabled")),
            )
        )
        return view

    def __init__(self, **traits):
        super(BasePlot, self).__init__(**traits)
        # Customize plot data and main plot based on any method
        # implementations provided by subclasses. Must be performed
        # after _plot_data and _plot default traits are assigned
        self.customize_plot_data(self._plot_data)
        self.customize_plot(self._plot)

    # --------------------
    # Defaults and getters
    # --------------------

    def __component_default(self):
        """The _plot trait containing a 2D view of the MCO data is chosen
        to be the TraitsUI view by default. This may be overridden in the
        create_plot method for more complicated layouts.
        """
        return self._plot

    def __plot_default(self):
        plot = ChacoPlot(self._plot_data)
        # recenter_plot() requires self._plot to be defined
        do_later(self.recenter_plot)
        return plot

    def __plot_data_default(self):
        """ Default trait setter for _plot_data. Creates empty plot data
        in three columns: x, y and color_by. Any additional data to be
        plotted can be introduced by extending the customize_plot_data
        method
        """
        plot_data = ArrayPlotData()
        for data in ['x', 'y']:
            plot_data.set_data(data, [])
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

    @on_trait_change("x")
    def _update_plot_x_axis(self):
        """ Listens to the changes of the x-axis name. Updates the
        displayed data and resets the plot x axis."""
        self._update_plot_x_data()
        self._recenter_x_axis()

    @on_trait_change("y")
    def _update_plot_y_axis(self):
        """ Listens to the changes of the y-axis name. Updates the
        displayed data and resets the plot y axis."""
        self._update_plot_y_data()
        self._recenter_y_axis()

    @on_trait_change("analysis_model:selected_step_indices")
    def update_selected_points(self):
        """ Updates the selected points in the plot according to the model """
        if self.analysis_model.selected_step_indices is None:
            self._axis.index.metadata["selections"] = []
        else:
            self._axis.index.metadata[
                "selections"
            ] = self.analysis_model.selected_step_indices

    @on_trait_change("_axis:index.metadata_changed")
    def update_model(self):
        """ Updates the model according to the selected point in the plot """
        selected_indices = self._axis.index.metadata.get(
            "selections", []
        )
        if len(selected_indices) == 0:
            self.analysis_model.selected_step_indices = None
        else:
            self.analysis_model.selected_step_indices = selected_indices

    # -----------------
    #  Private Methods
    # -----------------

    def _recenter_x_axis(self):
        """ Resets the bounds on the x-axis of the plot. If now x axis
        is specified, uses the default bounds (-1, 1). Otherwise, infers
        the bounds from the x-axis related data."""
        if self.x == "":
            bounds = (-1, 1)
        else:
            data = self._plot_data.get_data("x")
            bounds = self.calculate_axis_bounds(data)
        self._set_plot_x_range(self._plot, *bounds)
        self._reset_zoomtool(self._plot)
        return bounds

    def _recenter_y_axis(self):
        """ Resets the bounds on the x-axis of the plot. If now y axis
        is specified, uses the default bounds (-1, 1). Otherwise, infers
        the bounds from the y-axis related data."""
        if self.y == "":
            bounds = (-1, 1)
        else:
            data = self._plot_data.get_data("y")
            bounds = self.calculate_axis_bounds(data)
        self._set_plot_y_range(self._plot, *bounds)
        self._reset_zoomtool(self._plot)
        return bounds

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

    def _update_plot(self):
        """Refresh the plot's axes and data. """
        if (
            self.x == ""
            or self.y == ""
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

    def _reset_plot_fired(self):
        """ Event handler for :attr:`reset_plot`"""
        self.recenter_plot()

    def _set_plot_x_range(self, plot, lower_bound, upper_bound):
        """Will reset the plot range"""
        plot.range2d.x_range.low_setting = lower_bound
        plot.range2d.x_range.high_setting = upper_bound

    def _set_plot_y_range(self, plot, lower_bound, upper_bound):
        plot.range2d.y_range.low_setting = lower_bound
        plot.range2d.y_range.high_setting = upper_bound

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
        self._set_plot_x_range(self._plot, x_low, x_high)
        self._set_plot_y_range(self._plot, y_low, y_high)

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

    def _reset_zoomtool(self, plot):
        # Replace the old ZoomTool as retaining the same one can lead
        # to issues where the zoom out/in limit is not reset on
        # resizing the plot.
        for idx, overlay in enumerate(plot.overlays):
            if isinstance(overlay, ZoomTool):
                plot.overlays[idx] = ZoomTool(plot)

    # ----------------
    #  Public Methods
    # ----------------

    def customize_plot(self, plot):
        """Create all overlayed plots required for the data view.

        There are three additional attributes that may be assigned during this
        method:

        _component: A reference to the Chaco Component object that will be
            displayed in the TraitsUI view. This can be the same as the _plot
            trait if a single plot is being viewed
        _axis: A reference to the Chaco BaseXYPlot object that holds the data
            points to be synchronized with selection of rows in the MCO data
            table
        _sub_axes: Dictionary containing additional references to overlayed
            plot axes that are not hooked up to the MCO data table

        Parameters
        ----------
        plot: ChacoPlot
            A reference to the Chaco Plot object that displays the data
            returned by the MCO in a 2D X and Y plot.
        """

    def customize_plot_data(self, plot_data):
        """Auxiliary method used to include more data sets in the plot.
        Can be overridden by inheriting classes to deal with more complex
        plot data.

        Parameters
        ----------
        plot_data: ArrayPlotData
            List of strings that refer to variables in the plot data
        """

    def update_data_view(self):
        """ Update the plot if an update was required. This function is a
        callback for the _plot_updater timer.
        """
        self._update_plot()
        self._reset_zoomtool(self._plot)

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

    def recenter_plot(self):
        """ Sets the size of the current plot to have some spacing
        between the largest/smallest value and the plot edge.
        """
        x_bounds = self._recenter_x_axis()
        y_bounds = self._recenter_y_axis()
        return (*x_bounds, *y_bounds)
