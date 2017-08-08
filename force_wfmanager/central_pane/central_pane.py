from pyface.tasks.api import TraitsTaskPane

from traits.api import Instance, on_trait_change

from traitsui.api import View, Tabbed, VGroup, UItem

from .analysis_model import AnalysisModel
from .plot import Plot
from .result_table import ResultTable


class CentralPane(TraitsTaskPane):
    id = 'force_wfmanager.central_pane'
    name = 'Central Pane'

    #: The model for the analysis part
    analysis_model = Instance(AnalysisModel)

    #: The table in which we display the computation results received from the
    #: bdss
    result_table = Instance(ResultTable)

    #: The plot view
    plot = Instance(Plot)

    view = View(Tabbed(
        VGroup(
            UItem(name='result_table', style='custom'),
            label='Result Table'
        ),
        VGroup(
            UItem('plot', style='custom'),
            label='Plot'
        )
    ))

    @on_trait_change('analysis_model.evaluation_steps[]')
    def update_views(self):
        self.result_table.evaluation_steps = \
            self.analysis_model.evaluation_steps
        self.plot.evaluation_steps = self.analysis_model.evaluation_steps

    def _analysis_model_default(self):
        return AnalysisModel()

    def _result_table_default(self):
        return ResultTable(
            value_names=self.analysis_model.value_names,
            evaluation_steps=self.analysis_model.evaluation_steps
        )

    def _plot_default(self):
        return Plot(
            value_names=self.analysis_model.value_names,
            evaluation_steps=self.analysis_model.evaluation_steps
        )
