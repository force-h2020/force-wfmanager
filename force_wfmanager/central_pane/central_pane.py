from traits.api import Instance, Bool, Button, on_trait_change

from traitsui.api import View, Tabbed, VGroup, UItem

from pyface.tasks.api import TraitsTaskPane

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

    #: Enable or disable the contained entities.
    #: Used when the computation is running
    enabled = Bool(True)

    #: Button used to clear the model
    clear_button = Button('Clear')

    view = View(
        VGroup(
            Tabbed(
                VGroup(
                    UItem(name='result_table', style='custom'),
                    label='Result Table'),
                VGroup(
                    UItem('plot', style='custom'),
                    label='Plot'),
            ),
            VGroup(
                UItem('clear_button', enabled_when='enabled')
            )
        ),
    )

    def __init__(self, analysis_model, *args, **kwargs):
        super(CentralPane, self).__init__(*args, **kwargs)
        self.analysis_model = analysis_model

    def _result_table_default(self):
        return ResultTable(
            analysis_model=self.analysis_model
        )

    def _plot_default(self):
        return Plot(
            analysis_model=self.analysis_model
        )

    @on_trait_change('clear_button')
    def clear_model(self):
        self.analysis_model.clear_steps()
