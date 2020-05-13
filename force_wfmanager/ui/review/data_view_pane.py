#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

from pyface.tasks.api import TraitsTaskPane
from traits.api import (
    Button,
    Dict,
    Enum,
    Instance,
    List,
    on_trait_change,
    Type,
    Str,
)
from traitsui.api import EnumEditor, HGroup, UItem, VGroup, View

from force_wfmanager.model.analysis_model import AnalysisModel
from force_wfmanager.ui.review.plot import Plot
from force_wfmanager.ui.review.base_data_view import BaseDataView
from force_wfmanager.ui.ui_utils import class_description


class DataViewPane(TraitsTaskPane):
    """ A pane that contains a BaseDataView and the option to change it."""

    #: The analysis model containing the results
    analysis_model = Instance(AnalysisModel)

    # ------------------
    # Regular Attributes
    # ------------------

    #: An internal identifier for this pane
    id = "force_wfmanager.data_view_pane"

    #: The data view being displayed
    data_view = Instance(BaseDataView)

    #: Saved instances of data views from this session (this is used to store
    #: the settings from each data_view while the user tries other options)
    data_view_instances = Dict(Type(BaseDataView), Instance(BaseDataView))

    #: Button to change the data_view
    change_view = Button("Change graph type")

    #: Available data views contributed by the plugins
    available_data_views = List(Type(BaseDataView))

    #: Selected data view class (from the list above)
    data_view_selection = Enum(values="available_data_views")

    #: Human readable descriptions of each data view, for the UI
    data_view_descriptions = Dict(Type(BaseDataView), Str())

    #: Modal view for changing the selected plot
    selection_changer = View(
        HGroup(
            UItem(
                "data_view_selection",
                editor=EnumEditor(name="data_view_descriptions"),
                style="custom",
            ),
            label="Graph type",
            show_border=True,
        ),
        # NOTE: Making the dialog resizable is a (less than optimal) workaround
        # for a visualization issue on MacOS: see enthought/traitsui#587
        resizable=True,
        kind="livemodal",
    )

    #: View
    traits_view = View(
        VGroup(
            VGroup(UItem("change_view")), UItem("data_view", style="custom")
        )
    )

    def _data_view_default(self):
        plot_data_view = Plot(analysis_model=self.analysis_model)
        plot_data_view.is_active_view = True
        return plot_data_view

    def _available_data_views_default(self):
        """ Look through all the loaded plugins and try
        to extract their custom data views.

        """
        # "Plot" is added first as it serves as the default selection.
        available_data_views = [Plot]
        if self.task is not None and self.task.window is not None:
            # This is skipped if the current class is instantiated outside
            # of an application (e.g. specific tests)
            for plugin in self.task.window.application.plugin_manager:
                try:
                    available_data_views.extend(plugin.get_data_views())
                except AttributeError:
                    pass
        return available_data_views

    def update_descriptions(self, maxlength=80):
        descriptions = []
        for item in self.available_data_views:
            descriptions.append((item, class_description(item)))

        self.data_view_descriptions = dict(descriptions)

    def _change_view_fired(self):
        self.update_descriptions()
        self.edit_traits(view="selection_changer")

    @on_trait_change("data_view_selection")
    def switch_data_view(self, data_view_type):
        # Store current instance
        current_type = type(self.data_view)
        if current_type not in self.data_view_instances:
            self.data_view_instances[current_type] = self.data_view
        self.data_view.is_active_view = False

        # Retrieve or instantiate the requested type
        try:
            self.data_view = self.data_view_instances[data_view_type]
        except KeyError:
            self.data_view = data_view_type(analysis_model=self.analysis_model)
        self.data_view.is_active_view = True
