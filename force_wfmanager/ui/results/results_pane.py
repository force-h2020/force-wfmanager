from pyface.tasks.api import TraitsDockPane
from traits.api import Instance
from traitsui.api import VGroup, View, UItem

from force_wfmanager.model.analysis_model import AnalysisModel
from force_wfmanager.ui.results.result_table import ResultTable


class ResultsPane(TraitsDockPane):
    """ A TraitsDockPane which displays a ResultTable in the UI."""

    # -------------------
    # Required Attributes
    # -------------------

    #: The analysis model containing the results
    analysis_model = Instance(AnalysisModel)

    # ------------------
    # Regular Attributes
    # ------------------

    #: An internal identifier for this pane
    id = 'force_wfmanager.results_pane'

    #: Name displayed as the title of this pane
    name = 'Results Table'

    #: Remove the possibility to close the pane
    closable = False

    #: Remove the possibility to detach the pane from the GUI
    floatable = False

    #: Remove the possibility to move the pane in the GUI
    movable = True

    #: Make the pane visible by default
    visible = True

    # --------------------
    # Dependent Attributes
    # --------------------

    #: The table displaying the results.
    #: Listens to: :attr:`analysis_model`
    result_table = Instance(ResultTable)

    # ----
    # View
    # ----

    traits_view = View(VGroup(
        UItem('result_table', style='custom'),
    ))

    # Defaults

    def _result_table_default(self):
        return ResultTable(
            analysis_model=self.analysis_model
        )
