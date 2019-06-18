from pyface.tasks.api import TraitsDockPane
from traits.api import Instance
from traitsui.api import VGroup, View, UItem

from force_wfmanager.model.analysis_model import AnalysisModel
from force_wfmanager.ui.review.results_table import ResultsTable


class ResultsPane(TraitsDockPane):
    """ A TraitsDockPane which displays a ResultsTable in the UI."""

    # -------------------
    # Required Attributes
    # -------------------

    #: The analysis model containing the review
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

    #: The table displaying the review.
    #: Listens to: :attr:`analysis_model`
    results_table = Instance(ResultsTable)

    # ----
    # View
    # ----

    traits_view = View(VGroup(
        UItem('results_table', style='custom'),
    ))

    # Defaults

    def _results_table_default(self):
        return ResultsTable(
            analysis_model=self.analysis_model
        )
