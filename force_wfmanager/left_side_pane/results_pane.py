from pyface.tasks.api import TraitsDockPane

from traits.api import Instance

from traitsui.api import View, UItem, VGroup

from force_wfmanager.central_pane.result_table import ResultTable
from force_wfmanager.central_pane.analysis_model import AnalysisModel


class ResultsPane(TraitsDockPane):
    """ Side pane which contains the WorkflowSettings (Tree editor for the
    Workflow) and the Run button """

    id = 'force_wfmanager.results_pane'
    name = 'Workflow'

    #: Remove the possibility to close the pane
    closable = False

    #: Remove the possibility to detach the pane from the GUI
    floatable = False

    #: Remove the possibility to move the pane in the GUI
    movable = False

    #: Make the pane visible by default
    visible = True

    #: The table displaying the results
    result_table = Instance(ResultTable)

    #: The analysis model containing the results
    analysis_model = Instance(AnalysisModel)

    traits_view = View(VGroup(
        UItem('result_table', style='custom'),
    ))

    def _result_table_default(self):
        return ResultTable(
            analysis_model=self.analysis_model
        )
