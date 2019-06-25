from pyface.tasks.api import TraitsTaskPane
from traits.api import Instance
from traitsui.api import UItem, View, VGroup

from force_wfmanager.model.analysis_model import AnalysisModel
from force_wfmanager.ui.review.plot import Plot


class GraphPane(TraitsTaskPane):

    # -------------------
    # Required Attributes
    # -------------------

    #: The model for the analysis part
    analysis_model = Instance(AnalysisModel)

    # ------------------
    # Regular Attributes
    # ------------------

    #: An internal identifier for this pane
    id = 'force_wfmanager.graph_pane'

    #: Name displayed as the title of this pane
    name = 'Graph Pane'

    #: The plot view
    plot = Instance(Plot)

    # ----
    # View
    # ----

    view = View(VGroup(
        UItem('plot', style='custom'),
    ))

    def __init__(self, analysis_model, *args, **kwargs):
        super(GraphPane, self).__init__(*args, **kwargs)
        self.analysis_model = analysis_model

    def _plot_default(self):
        # by default, this pane displays the full
        # colourmapped scatter plot
        return Plot(
            analysis_model=self.analysis_model
        )
