from pyface.tasks.api import TraitsTaskPane
from traits.api import Instance, on_trait_change
from traitsui.api import VGroup, View, UItem

from force_wfmanager.model.analysis_model import AnalysisModel
from force_wfmanager.ui.review.plot import BasePlot
from force_wfmanager.ui.review.data_view import BaseDataView


class DataViewPane(TraitsTaskPane):
    """ A TraitsTaskPane that contains the selected BaseDataView."""

    #: The analysis model containing the results
    analysis_model = Instance(AnalysisModel)

    # ------------------
    # Regular Attributes
    # ------------------

    #: An internal identifier for this pane
    id = 'force_wfmanager.data_view_pane'

    #: Make the pane visible by default
    data_view = Instance(BaseDataView)

    def default_traits_view(self):
        view = View(VGroup(
            UItem('data_view', style='custom')
        ))
        return view

    def _data_view_default(self):
        return BasePlot(analysis_model=self.analysis_model)

    @on_trait_change('task.setup_task.selected_data_view')
    def sync_selected_data_view(self, data_view):
        self.data_view = data_view(analysis_model=self.analysis_model)
