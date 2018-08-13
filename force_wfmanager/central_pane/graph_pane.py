from pyface.tasks.api import TraitsTaskPane

from traits.api import Instance, Dict

from traitsui.api import View, VGroup, UItem
from traitsui.editors import ShellEditor

from .analysis_model import AnalysisModel
from .plot import Plot


class GraphPane(TraitsTaskPane):
    id = 'force_wfmanager.graph_pane'
    name = 'Graph Pane'

    #: The model for the analysis part
    analysis_model = Instance(AnalysisModel)

    #: The plot view
    plot = Instance(Plot)

    # Namespace for the console
    console_ns = Dict()

    view = View(VGroup(
            UItem('plot', style='custom'),
            UItem("console_ns", label="Console", editor=ShellEditor()),
            layout='tabbed'
    ))

    def __init__(self, analysis_model, *args, **kwargs):
        super(GraphPane, self).__init__(*args, **kwargs)
        self.analysis_model = analysis_model

    def _plot_default(self):
        return Plot(
            analysis_model=self.analysis_model
        )

    def _console_ns_default(self):
        namespace = {
            "task": self.task
        }
        try:
            namespace["app"] = self.task.window.application
        except AttributeError:
            namespace["app"] = None

        return namespace
