from pyface.tasks.api import TraitsTaskPane

from traits.api import Instance

from traitsui.api import View, VGroup, UItem

from force_wfmanager.api import AnalysisModel, Plot


class GraphPane(TraitsTaskPane):
    id = 'force_wfmanager.graph_pane'
    name = 'Graph Pane'

    #: The model for the analysis part
    analysis_model = Instance(AnalysisModel)

    #: The plot view
    plot = Instance(Plot)

    view = View(VGroup(
            UItem('plot', style='custom'),
    ))

    def __init__(self, analysis_model, *args, **kwargs):
        super(GraphPane, self).__init__(*args, **kwargs)
        self.analysis_model = analysis_model

    def _plot_default(self):
        return Plot(
            analysis_model=self.analysis_model
        )
