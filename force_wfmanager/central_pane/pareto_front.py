from traits.api import HasStrictTraits, List, Str, Tuple, Instance

from traitsui.api import View, UItem

from enable.api import Component, ComponentEditor

from chaco.api import ArrayPlotData, Plot


class ParetoFront(HasStrictTraits):
    #: List of parameter names
    value_names = List(Str)

    #: List of evaluation steps
    evaluation_steps = List(Tuple())

    #: The Pareto Front plot
    plot = Instance(Component)

    view = View(UItem('plot', editor=ComponentEditor(size=(300, 300))))

    def _plot_default(self):
        plot_data = ArrayPlotData()
        plot_data.set_data("x", [1, 2, 3])
        plot_data.set_data("y", [1.2, 0.56, 2.32])

        # Create the plot
        plot = Plot(plot_data)
        plot.plot(("x", "y"),
                  type="scatter",
                  name="Pareto Front",
                  marker="circle",
                  index_sort="ascending",
                  color="red",
                  marker_size=4,
                  bgcolor="white")

        plot.title = "Pareto Front"
        plot.line_width = 1
        plot.padding = 50

        return plot
