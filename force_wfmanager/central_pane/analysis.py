from pyface.tasks.api import TraitsTaskPane

from traits.api import List, Str, Tuple, Int, Instance

from traitsui.api import View, Tabbed, VGroup, Spring, UItem

from .pareto_front import ParetoFront


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

    view = View(Tabbed(
        VGroup(
            Spring(),
            label='Result Table'
        ),
        VGroup(
            UItem('pareto_front', style='custom'),
            label='Pareto Front'
        )
    ))

    def _pareto_front_default(self):
        return ParetoFront()
