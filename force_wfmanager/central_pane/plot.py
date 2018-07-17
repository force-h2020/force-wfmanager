from traits.api import (HasStrictTraits, List, Instance, Enum, Tuple,
                        on_trait_change, Button, Bool, Property)

from traitsui.api import View, UItem, Item, VGroup, HGroup

from enable.api import Component, ComponentEditor

from chaco.api import ArrayPlotData, ScatterInspectorOverlay, ArrayDataSource
from chaco.api import Plot as ChacoPlot
from chaco.tools.api import PanTool, ZoomTool, ScatterInspector

from .analysis_model import AnalysisModel


class Plot(HasStrictTraits):
    #: The model for the plot
    analysis_model = Instance(AnalysisModel, allow_none=False)

    _value_names = Tuple()

    #: First parameter used for the plot
    x = Enum(values='_value_names')

    #: Second parameter used for the plot
    y = Enum(values='_value_names')

    #: List containing the data arrays
    _data_arrays = List(List())

    #: The plot data. This is the model of the actual Chaco plot.
    _plot_data = Instance(ArrayPlotData)

    #: The 2D plot
    _plot = Instance(Component)

    #: Datasource of the plot (used for selection handling)
    _plot_index_datasource = Instance(ArrayDataSource)

    #: Button to reset plot view
    reset_plot = Button('Reset View')

    reset_enabled = Property(Bool(False), depends_on="_plot_data")

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

        plot.set(title="Plot", padding=50, line_width=1)

        # Add pan and zoom tools
        plot.tools.append(PanTool(plot))
        plot.overlays.append(ZoomTool(plot))

        # Add the selection tool
        scatter_plot.tools.append(ScatterInspector(
            scatter_plot,
            threshold=10,
            selection_mode="single",
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
        self._plot_index_datasource = scatter_plot.index

        return plot

    def __plot_data_default(self):
        plot_data = ArrayPlotData()
        plot_data.set_data('x', [])
        plot_data.set_data('y', [])
        return plot_data

    def __data_arrays_default(self):
        return [[] for _ in range(len(self.analysis_model.value_names))]

    @on_trait_change('analysis_model.value_names')
    def update_value_names(self):
        self._value_names = self.analysis_model.value_names
        # If there is more than one value names, we select the second one for
        # the y axis
        if len(self._value_names) > 1:
            self.y = self._value_names[1]

        # If there are no available value names, set the plot view to a default
        # state. This occurs when the analysis model is cleared.

        if self._value_names == ():
            self.set_plot_range(-1, 1, -1, 1)

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

    @on_trait_change('x,y')
    def _update_plot_data(self):
        """Set the plot data model to the appropriate arrays so that they
        can be displayed when either X or Y selections have been changed.
        """
        if self.x is None or self.y is None:
            self._plot_data.set_data('x', [])
            self._plot_data.set_data('y', [])
            return

        x_index = self.analysis_model.value_names.index(self.x)
        y_index = self.analysis_model.value_names.index(self.y)

        if self._data_arrays != []:
            self._plot_data.set_data('x', self._data_arrays[x_index])
            self._plot_data.set_data('y', self._data_arrays[y_index])

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

            self.set_plot_range(x_min, x_max, y_min, y_max)

            return x_min, x_max, y_min, y_max
        return None

    @on_trait_change('analysis_model.selected_step_index')
    def update_selected_point(self):
        """ Updates the selected point in the plot according to the model """
        if self.analysis_model.selected_step_index is None:
            self._plot_index_datasource.metadata['selections'] = []
        else:
            self._plot_index_datasource.metadata['selections'] = \
                [self.analysis_model.selected_step_index]

    @on_trait_change('_plot_index_datasource.metadata_changed')
    def update_model(self):
        """ Updates the model according to the selected point in the plot """
        selected_indices = self._plot_index_datasource.metadata.get(
            'selections', [])
        if len(selected_indices) == 0:
            self.analysis_model.selected_step_index = None
        else:
            self.analysis_model.selected_step_index = selected_indices[0]

    @on_trait_change('reset_plot')
    def reset_pressed(self):
        self.resize_plot()

    def _get_reset_enabled(self):
        x_data = self._plot_data.get_data('x')
        if len(x_data) > 1:
            return True
        return False

    def set_plot_range(self, x_low, x_high, y_low, y_high):
        """Helper method to set the size of the current _plot"""
        self._plot.range2d.x_range.low = x_low
        self._plot.range2d.x_range.high = x_high
        self._plot.range2d.y_range.low = y_low
        self._plot.range2d.y_range.high = y_high
