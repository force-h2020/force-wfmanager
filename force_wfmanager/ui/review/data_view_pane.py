from pyface.tasks.api import TraitsDockPane
from traits.api import Instance
from traitsui.api import VGroup, View, UItem

from force_wfmanager.model.analysis_model import AnalysisModel
from force_wfmanager.ui.review.plot import BasePlot
from force_wfmanager.ui.review.data_view import BaseDataView


class DataViewPane(TraitsDockPane):
    """ A TraitsDockPane that displays arbitrary contributed DataView
    objects in the UI.

    """
    #: The analysis model containing the results
    analysis_model = Instance(AnalysisModel)

    # ------------------
    # Regular Attributes
    # ------------------

    #: An internal identifier for this pane
    id = 'force_wfmanager.data_view_pane'

    #: Name displayed as the title of this pane
    name = 'Default Data View Pane'

    #: Description displayed in the selector dropdown
    description = 'Default Data View Pane'

    #: Remove the possibility to close the pane
    closable = False

    #: Remove the possibility to detach the pane from the GUI
    floatable = False

    #: Remove the possibility to move the pane in the GUI
    movable = True

    #: Make the pane visible by default
    data_view = Instance(BaseDataView)

    view = View(VGroup(
        UItem('data_view', style='custom')
    ))

    def _data_view_default(self):
        return BasePlot(analysis_model=self.analysis_model)
