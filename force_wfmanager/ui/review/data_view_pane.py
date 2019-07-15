from pyface.tasks.api import TraitsTaskPane
from traits.api import (
    Button, Dict, Enum, Instance, List, on_trait_change, Type, Unicode)
from traitsui.api import EnumEditor, HGroup, UItem, VGroup, View

from force_wfmanager.model.analysis_model import AnalysisModel
from force_wfmanager.ui.review.plot import Plot
from force_wfmanager.ui.review.data_view import BaseDataView


class DataViewPane(TraitsTaskPane):
    """ A pane that contains a BaseDataView and the option to change it."""

    #: The analysis model containing the results
    analysis_model = Instance(AnalysisModel)

    # ------------------
    # Regular Attributes
    # ------------------

    #: An internal identifier for this pane
    id = 'force_wfmanager.data_view_pane'

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
    data_view_descriptions = Dict(Type(BaseDataView), Unicode())

    selection_changer = View(
        HGroup(
            UItem(
                "data_view_selection",
                editor=EnumEditor(name='data_view_descriptions'),
                style="custom",
            ),
            label="Graph type",
            show_border=True
        ),
    )

    #: View
    traits_view = View(VGroup(
            VGroup(
                UItem('change_view'),
            ),
            UItem('data_view', style='custom')
        ))

    def _data_view_default(self):
        return Plot(analysis_model=self.analysis_model)

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

        def shorten(string, maxlength):
            if string.startswith("<class '"):

                # Usual str(type) of the form <class 'foo.bar.baz'>:
                # Remove wrapping and truncate, giving precedence to extremes.
                words = string[8:-2].split(".")
                num_words = len(words)
                word_priority = [
                    # from the out inwards, precedence to the left: 0 2 ... 3 1
                    min(2*i, 2*num_words - 2*i - 1) for i in range(num_words)]
                for threshold in range(num_words, 0, -1):
                    string = ""
                    for i, word in enumerate(words):
                        string += word if word_priority[i] < threshold else ""
                        string += "."
                    if len(string) <= maxlength + 1:
                        return string[:-1]
                # fallback when every dot-based truncation is too long.
                return shorten(words[0], maxlength)

            else:

                # Custom description: just truncate.
                return string if len(string) <= maxlength \
                    else string[:maxlength-3]+"..."

        descriptions = []
        for item in self.available_data_views:
            length = maxlength
            if hasattr(item, "description") and item.description is not None:
                item_description = shorten(item.description, length)
                # if there's enough room left, add the class name in brackets.
                length -= len(item_description) + 3
                if length >= 10:
                    item_description += " (" + shorten(str(item), length) + ")"
            else:
                item_description = shorten(str(item), length)
            descriptions.append((item, item_description))

        self.data_view_descriptions = dict(descriptions)

    def _change_view_fired(self):
        self.update_descriptions()
        self.edit_traits(view="selection_changer")

    @on_trait_change('data_view_selection')
    def switch_data_view(self, data_view_type):
        # Store current instance
        current_type = type(self.data_view)
        if current_type not in self.data_view_instances:
            self.data_view_instances[current_type] = self.data_view

        # Retrieve or instantiate the requested type
        try:
            self.data_view = self.data_view_instances[data_view_type]
        except KeyError:
            self.data_view = data_view_type(analysis_model=self.analysis_model)
