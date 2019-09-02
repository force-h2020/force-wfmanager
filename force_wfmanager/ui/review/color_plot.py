""" This submodule implements the following :class:`BaseDataView` subclasses:

* :class:`ColorPlot` extends :class:`BasePlot` to allow for an
  optional colourmap to be applied to a third variable.

"""
from chaco.api import Plot as ChacoPlot
from chaco.api import ColormappedScatterPlot
from chaco.default_colormaps import color_map_name_dict
from chaco.tools.api import PanTool, ZoomTool
from enable.api import ComponentEditor
from traits.api import (
    Button, Bool, Dict, Enum, List, on_trait_change
)
from traitsui.api import HGroup, Item, UItem, VGroup, View

from .base_plot import BasePlot


class ColorPlot(BasePlot):
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
    description = "ColorPlot with colormap"

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
            name="ColorPlot",
            marker="circle",
            fill_alpha=0.8,
            color_mapper=self._available_colormaps[self.colormap],
            marker_size=4,
            outline_color="black",
            index_sort="ascending",
            line_width=0,
            bgcolor="white")[0]

        plot.trait_set(title="ColorPlot", padding=75, line_width=1)

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
