""" This submodule implements the following :class:`BaseDataView` subclasses:

* :class:`BasePlot` provides a simple 2D scatter plot over the columns from
  the analysis model, with x and y selectable with a dropdown. It updates when
  new data is incoming, with a 1 second timer to avoid continuous updates.
  It is not selectable and is meant as a template for subclassing.
* :class:`Plot` extends :class:`BasePlot` to allow for an
  optional colourmap to be applied to a third variable.

"""

from chaco.api import ArrayPlotData, ArrayDataSource, ScatterInspectorOverlay
from chaco.api import Plot as ChacoPlot
from chaco.api import BaseXYPlot, ColormappedScatterPlot
from chaco.default_colormaps import color_map_name_dict
from pyface.timer.api import CallbackTimer, do_later
from chaco.tools.api import PanTool, ScatterInspector, ZoomTool
from enable.api import Component, ComponentEditor
from enable.api import KeySpec
from traits.api import (
    Button, Bool, Dict, Enum, Instance, List, Property, Tuple,
    on_trait_change, Unicode
)
from traitsui.api import HGroup, Item, UItem, VGroup, View

from .data_view import BaseDataView


class BasePlot(BaseDataView):
    """Simple 2D scatter plot (see module-level doc)."""

    # -------------------
    # Required Attributes
    # -------------------

    #: Button to reset plot view. The button is active if :attr:`reset_enabled`
    #: is *True* and inactive if it is *False*.
    reset_plot = Button('Reset View')

    #: First parameter used for the plot (abscissa)
    x = Enum(values='_value_names')

    #: Second parameter used for the plot (ordinate)
    y = Enum(values='_value_names')

    #: Optional third parameter used to set colour of points
    color_by = Enum(values='_value_names')

    #: Optional title to display above the figure
    title = Unicode('Plot')

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

    #: A local copy of the analysis model's value names
    #: Listens to: :attr:`ç.value_names
    #: <force_wfmanager.central_pane.analysis_model.AnalysisModel.value_names>`
    _value_names = Tuple()

    #: List containing the data arrays.
    #: Listens to: :attr:`analysis_model.value_names
    #: <force_wfmanager.central_pane.analysis_model.AnalysisModel.value_names>`
    #: , :attr:`analysis_model.evaluation_steps
    #: <force_wfmanager.central_pane.analysis_model.AnalysisModel.\
    #: evaluation_steps>`
    _data_arrays = List(List())

    #: The plot data. This is the model of the actual Chaco plot.
    #: Listens to: :attr:`x`, :attr:`y`
    _plot_data = Instance(ArrayPlotData)

    #: Timer to check on required updates
    plot_updater = Instance(CallbackTimer)

    #: Schedule a refresh of plot data and axes
    update_required = Bool(False)

    # ------------------
    # Regular Attributes
    # ------------------

    #: Short description for the UI selection
    description = "Simple plot"

    # ----
    # View
    # ----

    view = View(
        VGroup(
            HGroup(
                Item('x'),
                Item('y'),
            ),
            UItem('_plot', editor=ComponentEditor()),
            VGroup(
                UItem('reset_plot', enabled_when='reset_enabled')
            )
        )
    )

    # --------------------
    # Defaults and getters
    # --------------------

    def _plot_updater_default(self):
        return CallbackTimer.timer(
            interval=1, callback=self._check_scheduled_updates)

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
            selection_mode="multi"
        )

        overlay = ScatterInspectorOverlay(
            scatter_plot,
            hover_color=(0, 0, 1, 1),
            hover_marker_size=6,
            selection_marker_size=20,
            selection_color=(0, 0, 1, 0.5),
            selection_outline_color=(0, 0, 0, 0.8),
            selection_line_width=3)

        return inspector, overlay

    def plot_scatter(self):
        plot = ChacoPlot(self._plot_data)
        scatter_plot = plot.plot(
            ('x', 'y'),
            type="scatter",
            name="Plot",
            marker="circle",
            index_sort="ascending",
            color="green",
            marker_size=4,
            bgcolor="white")[0]

        plot.trait_set(title=self.title, padding=75, line_width=1)

        # Add pan and zoom tools
        scatter_plot.tools.append(PanTool(plot))
        scatter_plot.overlays.append(ZoomTool(plot))

        # Set the scatterplot's default selection marker invisible as it
        # lead to artifacts on axis when switching between plotted cols
        scatter_plot.trait_set(selection_color=(0, 0, 0, 0),
                               selection_outline_color=(0, 0, 0, 0))

        # Add the selection tool
        inspector, overlay = self._get_scatter_inspector_overlay(
            scatter_plot)
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
        plot_data.set_data('x', [])
        plot_data.set_data('y', [])
        plot_data.set_data('color_by', [])
        return plot_data

    def __data_arrays_default(self):
        return [[] for _ in range(len(self.analysis_model.value_names))]

    # ----------
    # Properties
    # ----------

    #: NOTE: appears to be updated very often (could do with caching?)
    def _get_reset_enabled(self):
        x_data = self._plot_data.get_data('x')
        if len(x_data) > 0:
            return True
        return False

    # ---------
    # Listeners
    # ---------

    # Response to analysis model changes

    @on_trait_change('analysis_model.numerical_value_names')
    def update_value_names(self):
        """ Sets the value names in the plot to match those it the analysis
        model and resets any data arrays."""

        self._value_names = self.analysis_model.numerical_value_names
        self._data_arrays = self.__data_arrays_default()
        # If there is more than one value names, we select the second one for
        # the y axis
        if len(self._value_names) > 1:
            self.y = self._value_names[1]
        elif len(self._value_names) == 1:
            self.y = self._value_names[0]

        # If there are no available value names, set the plot view to a default
        # state. This occurs when the analysis model is cleared.

        if self._value_names == ():
            self._set_plot_range(-1, 1, -1, 1)
            # Unset the axis labels
            self._plot.x_axis.title = ""
            self._plot.y_axis.title = ""

        self._update_plot()

    @on_trait_change('analysis_model:evaluation_steps[]')
    def request_update(self):
        # Data points are being added: update plot data at the next cycle
        self.update_required = True

    # Response to user input

    @on_trait_change('is_active_view')
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

    @on_trait_change('x,y')
    def _update_plot(self):
        """Refresh the plot's axes and data. """
        if self.x is None or self.y is None \
                or self.color_by is None or self._data_arrays == []:
            self._plot_data.set_data('x', [])
            self._plot_data.set_data('y', [])
            self.recenter_plot()
            return

        x_index = self.analysis_model.value_names.index(self.x)
        y_index = self.analysis_model.value_names.index(self.y)
        c_index = self.analysis_model.value_names.index(self.color_by)

        # Set the axis labels
        self._plot.x_axis.title = self.x
        self._plot.y_axis.title = self.y

        data_arrays = self._data_arrays

        self._plot_data.set_data('x', data_arrays[x_index])
        self._plot_data.set_data('y', data_arrays[y_index])
        self._plot_data.set_data('color_by', data_arrays[c_index])

        self.recenter_plot()

    def update_data_arrays(self):
        """ Update the data arrays used by the plot. It assumes that the
        AnalysisModel object is valid. Which means that the number of
        value_names is equal to the number of element in each evaluation step
        (e.g. value_names=["viscosity", "pressure"] then each evaluation step
        is a two dimensions tuple). Only the number of evaluation
        steps can change, not their values.

        Note: evaluation steps is row-based (one tuple = one row). The data
        arrays are column based. The transformation happens here.
        """
        data_dim = len(self.analysis_model.value_names)

        # This can happen when the evaluation steps has been cleared, but the
        # value names are not updated yet
        if data_dim != len(self._value_names):
            self.update_value_names()

        # If there is no data yet, or the data has been removed, make sure the
        # plot is updated accordingly (empty arrays)
        if data_dim == 0:
            self._update_plot()
            return

        evaluation_steps = self.analysis_model.evaluation_steps.copy()

        # In this case, the value_names have changed, so we need to
        # synchronize the number of data arrays to the newly found data
        # dimensionality before adding new data to them. Of course, this also
        # means to remove the current content.
        if data_dim != len(self._data_arrays):
            self._data_arrays = [[] for _ in range(data_dim)]

        # If the number of evaluation steps is less than the number of element
        # in the data arrays, it certainly means that the model has been
        # reinitialized. The only thing we can do is recompute the data arrays.
        if len(evaluation_steps) < len(self._data_arrays[0]):
            for data_array in self._data_arrays:
                data_array[:] = []

        # Update the data arrays with the newly added evaluation_steps
        new_evaluation_steps = evaluation_steps[len(self._data_arrays[0]):]
        for evaluation_step in new_evaluation_steps:
            # Fan out the data in the appropriate arrays. The model guarantees
            # that the size of the evaluation step and the data_dim are the
            # same.
            for index in range(data_dim):
                self._data_arrays[index].append(evaluation_step[index])

    def _check_scheduled_updates(self):
        """ Update the plot if an update was required. This function is a
        callback for the _plot_updater timer.
        """
        if self.update_required:
            self.update_data_arrays()
            self._update_plot()
            self.update_required = False

    def _reset_plot_fired(self):
        """ Event handler for :attr:`reset_plot`"""
        self.recenter_plot()

    def recenter_plot(self):
        """ Sets the size of the current plot to have some spacing between the
        largest/smallest value and the plot edge. Also returns the new values
        (X min, X max, Y min, Y max) if the plot area changes or None if it
        does not.
        """
        if self.x is None or self.y is None:
            return None

        x_data = self._plot_data.get_data('x')
        y_data = self._plot_data.get_data('y')

        if len(x_data) > 1:
            x_max = max(x_data)
            x_min = min(x_data)
            x_size = abs(x_max - x_min)
            x_max = x_max + 0.1 * x_size
            x_min = x_min - 0.1 * x_size

            y_max = max(y_data)
            y_min = min(y_data)
            y_size = abs(y_max - y_min)
            y_max = y_max + 0.1 * abs(y_size)
            y_min = y_min - 0.1 * abs(y_size)

            self._set_plot_range(x_min, x_max, y_min, y_max)

            return x_min, x_max, y_min, y_max

        elif len(x_data) == 1:
            self._set_plot_range(x_data[0] - 0.5, x_data[0] + 0.5,
                                 y_data[0] - 0.5, y_data[0] + 0.5)
            # Replace the old ZoomTool as retaining the same one can lead
            # to issues where the zoom out/in limit is not reset on
            # resizing the plot.

            for idx, overlay in enumerate(self._plot.overlays):
                if isinstance(overlay, ZoomTool):
                    self._plot.overlays[idx] = ZoomTool(self._plot)

            return (x_data[0] - 0.5, x_data[0] + 0.5, y_data[0] - 0.5,
                    y_data[0] + 0.5)

        return None

    @on_trait_change('analysis_model.selected_step_indices')
    def update_selected_points(self):
        """ Updates the selected points in the plot according to the model """
        if self.analysis_model.selected_step_indices is None:
            self._plot_index_datasource.metadata['selections'] = []
        else:
            self._plot_index_datasource.metadata['selections'] = \
                self.analysis_model.selected_step_indices

    @on_trait_change('_plot_index_datasource.metadata_changed')
    def update_model(self):
        """ Updates the model according to the selected point in the plot """
        selected_indices = self._plot_index_datasource.metadata.get(
            'selections', [])
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
        self._plot.range2d.x_range.low_setting = x_low
        self._plot.range2d.x_range.high_setting = x_high
        self._plot.range2d.y_range.low_setting = y_low
        self._plot.range2d.y_range.high_setting = y_high

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
            self._plot.range2d.y_range.high_setting
        )


class Plot(BasePlot):
    """Simple 2D scatter plot with optional colormap (see module doc)."""

    # ------------------
    # Regular Attributes
    # ------------------

    #: Colour options button:
    color_options = Button('Color...')

    colormap = Enum(values='_available_colormaps_names',
                    depends_on='_available_colormaps_names')

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
    __continuous_colormaps_names = (
        ['viridis'] +
        [cmap_name
         for cmap_name in color_map_name_dict.keys()
         if cmap_name != 'viridis']
    )

    _available_colormaps = __continuous_colormaps
    _available_colormaps_names = List(__continuous_colormaps_names,
                                      depends_on='_available_colormaps')

    view = View(
        VGroup(
            HGroup(
                Item('x'),
                Item('y'),
                UItem('color_options'),
            ),
            UItem('_plot', editor=ComponentEditor()),
            VGroup(
                UItem('reset_plot', enabled_when='reset_enabled')
            )
        )
    )

    @on_trait_change('color_plot')
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

    @on_trait_change('colormap')
    def _update_cmap(self):
        cmap = self._available_colormaps[self.colormap]
        if isinstance(self._axis, ColormappedScatterPlot):
            _range = self._axis.color_mapper.range
            self._axis.color_mapper = cmap(_range)

    def _color_options_fired(self):
        """ Event handler for :attr:`color_options` button. """
        view = View(
            Item('color_plot'),
            Item('color_by', enabled_when='color_plot'),
            Item('colormap', enabled_when='color_plot'),
            kind='livemodal'
        )
        self.edit_traits(view=view)

    def plot_cmap_scatter(self):
        plot = ChacoPlot(self._plot_data)

        cmap_scatter_plot = plot.plot(
            ('x', 'y', 'color_by'),
            type="cmap_scatter",
            name="Plot",
            marker="circle",
            fill_alpha=0.8,
            color_mapper=self._available_colormaps[self.colormap],
            marker_size=4,
            outline_color="black",
            index_sort="ascending",
            line_width=0,
            bgcolor="white")[0]

        plot.trait_set(title="Plot", padding=75, line_width=1)

        # Add pan and zoom tools
        cmap_scatter_plot.tools.append(PanTool(plot))
        cmap_scatter_plot.overlays.append(ZoomTool(plot))

        # Add the selection tool
        inspector, overlay = self._get_scatter_inspector_overlay(
            cmap_scatter_plot)
        cmap_scatter_plot.tools.append(inspector)
        cmap_scatter_plot.overlays.append(overlay)

        self._plot_index_datasource = cmap_scatter_plot.index
        self._axis = cmap_scatter_plot

        return plot

    # Response to UI changes

    @on_trait_change('color_by')
    def _update_color_plot(self):
        if self.x is None or self.y is None \
                or self.color_by is None or self._data_arrays == []:
            self._plot_data.set_data('color_by', [])
            return

        c_index = self.analysis_model.value_names.index(self.color_by)
        self._plot_data.set_data('color_by', self._data_arrays[c_index])
        self._plot_data.set_data('color_by', self._data_arrays[c_index])
