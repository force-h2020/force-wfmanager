from traits.api import (HasStrictTraits, List, Instance, Enum, Property,
                        on_trait_change, Int)

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

    #: The 2D plot
    plot = Property(Instance(Component), depends_on=['x', 'y'])

    #: First parameter used for the plot
    x = Enum(values='analysis_model.value_names')

    #: Second parameter used for the plot
    y = Enum(values='analysis_model.value_names')

    view = View(VGroup(
        HGroup(
            Item('x'),
            Item('y'),
        ),
        UItem('plot', editor=ComponentEditor()),
    ))

    def _get_plot(self):
        if self.x is None or self.y is None:
            return None

        x_index = self.analysis_model.value_names.index(self.x)
        y_index = self.analysis_model.value_names.index(self.y)

        plot_data = ArrayPlotData()
        plot_data.set_data(self.x, self.data_arrays[x_index])
        plot_data.set_data(self.y, self.data_arrays[y_index])

        # Create the plot
        plot = ChacoPlot(plot_data)
        plot.plot((self.x, self.y),
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

    def _data_arrays_default(self):
        return self._compute_data_arrays()

    def _get_data_dim(self):
        return len(self.analysis_model.value_names)

    @on_trait_change('analysis_model.evaluation_steps')
    def update_data_arrays(self):
        self.data_arrays = self._compute_data_arrays()

    def _compute_data_arrays(self):
        data_arrays = self.data_dim*[[]]

        if len(self.analysis_model.evaluation_steps) == 0:
            return data_arrays

        for evaluation_step in self.analysis_model.evaluation_steps:
            for index in range(self.data_dim):
                data_arrays[index].append(evaluation_step[index])
        return data_arrays
