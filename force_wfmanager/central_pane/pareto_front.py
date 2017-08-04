from traits.api import (HasStrictTraits, List, Str, Tuple, Instance, Enum,
                        Property)

from traitsui.api import View, UItem, Item, VGroup, HGroup

from enable.api import Component, ComponentEditor

from chaco.api import ArrayPlotData, Plot


class ParetoFront(HasStrictTraits):
    #: List of parameter names
    value_names = List(Str)

    #: List of evaluation steps
    evaluation_steps = List(Tuple())

    #: List containing the data arrays
    data_arrays = List(List())

    #: The Pareto Front plot
    plot = Property(Instance(Component), depends_on=['x', 'y'])

    #: First parameter used for the plot
    x = Enum(values='value_names')

    #: Second parameter used for the plot
    y = Enum(values='value_names')

    view = View(VGroup(
        HGroup(
            Item('x'),
            Item('y'),
        ),
        UItem('plot', editor=ComponentEditor()),
    ))

    def _get_plot(self):
        x_index = self.value_names.index(self.x)
        y_index = self.value_names.index(self.y)

        plot_data = ArrayPlotData()
        plot_data.set_data(self.x, self.data_arrays[x_index])
        plot_data.set_data(self.y, self.data_arrays[y_index])

        # Create the plot
        plot = Plot(plot_data)
        plot.plot((self.x, self.y),
                  type="scatter",
                  name="Pareto Front",
                  marker="circle",
                  index_sort="ascending",
                  color="blue",
                  marker_size=4,
                  bgcolor="white")

        plot.title = "Pareto Front"
        plot.line_width = 1
        plot.padding = 50

        return plot

    def _data_arrays_default(self):
        data_dim = len(self.evaluation_steps[0])
        data_arrays = [[] for index in range(data_dim)]
        for evaluation_step in self.evaluation_steps:
            for index in range(data_dim):
                data_arrays[index].append(evaluation_step[index])
        return data_arrays
