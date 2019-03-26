from chaco.api import ArrayPlotData, ArrayDataSource, ScatterInspectorOverlay
from chaco.api import Plot as ChacoPlot
from chaco.tools.api import PanTool, ScatterInspector, ZoomTool
from enable.api import Component, ComponentEditor
from traits.api import (
    Button, Bool, Enum, HasStrictTraits, Instance, List, Property, Tuple,
    on_trait_change
)
from traitsui.api import HGroup, Item, UItem, VGroup, View

from .analysis_model import AnalysisModel


class Plot(HasStrictTraits):

    # -------------------
    # Required Attributes
    # -------------------

    #: The model for the plot
    analysis_model = Instance(AnalysisModel, allow_none=False)

    # ------------------
    # Regular Attributes
    # ------------------

    #: First parameter used for the plot
    x = Enum(values='_value_names')

    #: Second parameter used for the plot
    y = Enum(values='_value_names')

    #: Button to reset plot view. The button is active if :attr:`reset_enabled`
    #: is *True* and inactive if it is *False*.
    reset_plot = Button('Reset View')

    # --------------------
    # Dependent Attributes
    # --------------------

    #: The 2D plot
    #: Listens to: :attr:`x`, :attr:`y`
    _plot = Instance(Component)

    #: A local copy of the analysis model's value names
    #: Listens to: :attr:`analysis_model.value_names
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

    #: Datasource of the plot (used for selection handling)
    #: Listens to: :attr:`analysis_model.selected_step_indices
    #: <force_wfmanager.central_pane.analysis_model.AnalysisModel.\
    #: selected_step_indices>`
    _plot_indices_datasource = Instance(ArrayDataSource)

    # ----------
    # Properties
    # ----------

    #: Boolean indicating whether the plot view can be reset or not.
    reset_enabled = Property(Bool(), depends_on="_plot_data")

    # ----
    # View
    # ----

    view = View(VGroup(
        HGroup(
            Item('x'),
            Item('y'),
        ),
        UItem('_plot', editor=ComponentEditor()),
        VGroup(
            UItem('reset_plot', enabled_when='reset_enabled')
        )
    ))

    def __init__(self, analysis_model, *args, **kwargs):
        self.analysis_model = analysis_model
        super(Plot, self).__init__(*args, **kwargs)

        self.update_data_arrays()

    # Defaults

    def __plot_default(self):
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

        plot.set(title="Plot", padding=75, line_width=1)

        # Add pan and zoom tools
        plot.tools.append(PanTool(plot))
        plot.overlays.append(ZoomTool(plot))

        # Add the selection tool
        scatter_plot.tools.append(ScatterInspector(
            scatter_plot,
            threshold=10,
            selection_mode="multi",
        ))
        overlay = ScatterInspectorOverlay(
            scatter_plot,
            hover_color="blue",
            hover_marker_size=6,
            selection_marker_size=6,
            selection_color="blue",
            selection_outline_color="blue",
            selection_line_width=3)
        scatter_plot.overlays.append(overlay)

        # Initialize plot datasource
        self._plot_indices_datasource = scatter_plot.index

        return plot

    def __plot_data_default(self):
        plot_data = ArrayPlotData()
        plot_data.set_data('x', [])
        plot_data.set_data('y', [])
        return plot_data

    def __data_arrays_default(self):
        return [[] for _ in range(len(self.analysis_model.value_names))]

    # Properties

    def _get_reset_enabled(self):
        x_data = self._plot_data.get_data('x')
        if len(x_data) > 0:
            return True
        return False

    # Response to analysis model changes

    @on_trait_change('analysis_model.value_names')
    def update_value_names(self):
        """ Sets the value names in the plot to match those it the analysis
        model and resets any data arrays."""
        self._value_names = self.analysis_model.value_names
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

        self._update_plot_data()

    @on_trait_change('analysis_model.evaluation_steps[]')
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
            self._update_plot_data()
            return

        evaluation_steps = self.analysis_model.evaluation_steps

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

        # Update plot data
        self._update_plot_data()

    # Response to UI changes

    @on_trait_change('x,y')
    def _update_plot_data(self):
        """Set the plot data model to the appropriate arrays so that they
        can be displayed when either X or Y selections have been changed.
        """
        if self.x is None or self.y is None or self._data_arrays == []:
            self._plot_data.set_data('x', [])
            self._plot_data.set_data('y', [])
            return

        x_index = self.analysis_model.value_names.index(self.x)
        y_index = self.analysis_model.value_names.index(self.y)

        # Set the axis labels
        self._plot.x_axis.title = self.x
        self._plot.y_axis.title = self.y

        self._plot_data.set_data('x', self._data_arrays[x_index])
        self._plot_data.set_data('y', self._data_arrays[y_index])

        self.resize_plot()

    @on_trait_change('reset_plot')
    def reset_pressed(self):
        """ Event handler for :attr:`reset_plot`"""
        self.resize_plot()

    def resize_plot(self):
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
            self._plot_indices_datasource.metadata['selections'] = []
        else:
            self._plot_indices_datasource.metadata['selections'] = \
                self.analysis_model.selected_step_indices

    @on_trait_change('_plot_indices_datasource.metadata_changed')
    def update_model(self):
        """ Updates the model according to the selected point in the plot """
        selected_indices = self._plot_indices_datasource.metadata.get(
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
