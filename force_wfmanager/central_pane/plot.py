from traits.api import (HasStrictTraits, List, Instance, Enum, Property,
                        on_trait_change, Int, Str, Bool)

from traitsui.api import View, UItem, Item, VGroup, HGroup

from enable.api import Component, ComponentEditor

from chaco.api import ArrayPlotData
from chaco.api import Plot as ChacoPlot

from .analysis_model import AnalysisModel


class Plot(HasStrictTraits):
    #: The model for the plot
    analysis_model = Instance(AnalysisModel)

    #: Data dimension
    data_dim = Property(Int(), depends_on='analysis_model.value_names')

    #: List containing the data arrays
    data_arrays = List(List())

    #: The plot data
    plot_data = Instance(ArrayPlotData)

    #: The 2D plot
    plot = Instance(Component)

    #: Boolean defining if the plot if visible or not
    plot_visible = Bool(False)

    #: Possible plotted variables
    value_names = Property(
        List(Str),
        depends_on="analysis_model.value_names[]"
    )

    #: First parameter used for the plot
    x = Enum(values='value_names')

    #: Second parameter used for the plot
    y = Enum(values='value_names')

    view = View(VGroup(
        HGroup(
            Item('x'),
            Item('y'),
        ),
        UItem('plot', editor=ComponentEditor(), visible_when="plot_visible"),
    ))

    def __init__(self, analysis_model, *args, **kwargs):
        self.analysis_model = analysis_model

        super(Plot, self).__init__(*args, **kwargs)

        self.update_data_arrays()

    def _plot_default(self):
        plot = ChacoPlot(self.plot_data)

        plot.plot(
            ('x', 'y'),
            type="scatter",
            name="Plot",
            marker="circle",
            index_sort="ascending",
            color="blue",
            marker_size=4,
            bgcolor="white")

        plot.title = "Plot"
        plot.line_width = 1
        plot.padding = 50

        return plot

    def _get_value_names(self):
        # TODO: Filter value names per type (we do not support string
        # values for the plot)
        return self.analysis_model.value_names

    def _plot_data_default(self):
        plot_data = ArrayPlotData()
        plot_data.set_data('x', [])
        plot_data.set_data('y', [])
        return plot_data

    def _data_arrays_default(self):
        return [[] for _ in range(self.data_dim)]

    def _get_data_dim(self):
        return len(self.value_names)

    @on_trait_change('analysis_model.evaluation_steps[]')
    def update_data_arrays(self):
        """ Update the data arrays used by the plot. It assumes that the
        AnalysisModel object is valid. Which means that the number of
        value_names is equal to the number of element in each evaluation step
        (e.g. value_names=["viscosity", "pressure"] then each evaluation step
        is a two dimensions tuple). Only the number of evaluation
        steps can change, not their values. """
        # If there is no data yet, don't do anything
        if self.data_dim == 0:
            return

        evaluation_steps = self.analysis_model.evaluation_steps

        # If the number of evaluation steps is less than the number of element
        # in the data arrays, it certainly means that the model has been
        # reinitialized. The only thing we can do is recompute the data arrays.
        if len(evaluation_steps) < len(self.data_arrays[0]):
            for data_array in self.data_arrays:
                data_array[:] = []

        # Update the data arrays with the newly added evaluation_steps
        new_evaluation_steps = evaluation_steps[len(self.data_arrays[0]):]
        for evaluation_step in new_evaluation_steps:
            for index in range(self.data_dim):
                self.data_arrays[index].append(evaluation_step[index])

        # Update plot data
        self._update_plot_data()

    @on_trait_change('x,y')
    def _update_plot_data(self):
        if self.x is None or self.y is None:
            self.plot_visible = False
            self.plot_data.set_data('x', [])
            self.plot_data.set_data('y', [])
            return

        x_index = self.analysis_model.value_names.index(self.x)
        y_index = self.analysis_model.value_names.index(self.y)

        self.plot_data.set_data('x', self.data_arrays[x_index])
        self.plot_data.set_data('y', self.data_arrays[y_index])

        self.plot_visible = True
