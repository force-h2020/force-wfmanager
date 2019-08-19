from traits.api import Interface, Unicode


class IBasePlot(Interface):
    """ This is an example of a custom plot, that replaces
    the default scatter plot with a line plot.

    """

    title = Unicode()

    description = Unicode()

    def __plot_default(self):
        raise NotImplementedError
