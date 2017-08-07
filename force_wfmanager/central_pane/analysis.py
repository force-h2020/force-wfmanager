from pyface.tasks.api import TraitsTaskPane

from traits.api import List, Str, Tuple, Int, Instance, on_trait_change

from traitsui.api import View, Tabbed, VGroup, UItem

from .pareto_front import ParetoFront

from .result_table import ResultTable


class Analysis(TraitsTaskPane):
    id = 'force_wfmanager.analysis'
    name = 'Analysis'

    #: List of parameter names
    value_names = List(Str)

    #: Evaluation steps, each evalutation step is a tuple of parameter values,
    #: received from the bdss. Each value can be of any type. The order of
    #: the parameters in each evaluation step must match the order of
    #: value_names
    evaluation_steps = List(Tuple())

    #: Selected step, used for highlighting in the table/plot
    selected_step_index = Int(None)

    #: The Pareto Front view
    pareto_front = Instance(ParetoFront)

    #: The table in which we display the computation results received from the
    #: bdss
    result_table = Instance(ResultTable)

    view = View(Tabbed(
        VGroup(
            UItem(name='result_table', style='custom'),
            label='Result Table'
        ),
        VGroup(
            UItem('pareto_front', style='custom'),
            label='Pareto Front'
        )
    ))

    def _pareto_front_default(self):
        return ParetoFront(
            value_names=self.value_names,
            evaluation_steps=self.evaluation_steps
        )

    @on_trait_change('evaluation_steps[]')
    def update_pareto_front(self):
        self.pareto_front.evaluation_steps = self.evaluation_steps

    def _result_table_default(self):
        return ResultTable(
            value_names=self.value_names,
            evaluation_steps=self.evaluation_steps
        )
