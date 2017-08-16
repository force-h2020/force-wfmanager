from traits.api import (HasStrictTraits, List, Instance, Enum, Property,
                        on_trait_change)

from traitsui.api import View, UItem, Item, VGroup, HGroup

from enable.api import Component, ComponentEditor

from chaco.api import ArrayPlotData, ScatterInspectorOverlay
from chaco.api import Plot as ChacoPlot
from chaco.tools.api import PanTool, ZoomTool, ScatterInspector

from .analysis_model import AnalysisModel


class Plot(HasStrictTraits):
    #: The model for the plot
    analysis_model = Instance(AnalysisModel, allow_none=False)

    _value_names = Property(depends_on="analysis_model.value_names")

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

    view = View(VGroup(
        HGroup(
            Item('x'),
            Item('y'),
        ),
        UItem('_plot', editor=ComponentEditor()),
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
            color="blue",
            marker_size=4,
            bgcolor="white")

        plot.set(title="Plot", padding=50, line_width=1)

        plot.tools.append(PanTool(plot))
        plot.overlays.append(ZoomTool(plot))

        return plot

    def __plot_data_default(self):
        plot_data = ArrayPlotData()
        plot_data.set_data('x', [])
        plot_data.set_data('y', [])
        return plot_data

    def __data_arrays_default(self):
        return [[] for _ in range(len(self.analysis_model.value_names))]

    def _get__value_names(self):
        return self.analysis_model.value_names

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
        # If there is no data yet, or the data has been removed, make sure the
        # plot is updated accordingly and don't touch the data_arrays
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

        self._plot_data.set_data('x', self._data_arrays[x_index])
        self._plot_data.set_data('y', self._data_arrays[y_index])
