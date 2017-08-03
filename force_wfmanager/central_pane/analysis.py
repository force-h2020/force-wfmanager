from pyface.tasks.api import TraitsTaskPane

from traits.api import List, Str, Any, Int

from traitsui.api import View, Tabbed, VGroup, Spring


class Analysis(TraitsTaskPane):
    id = 'force_wfmanager.analysis'
    name = 'Analysis'

    #: List of parameter names
    value_names = List(Str)

    #: Evaluation steps, each evalutation step is a list of parameter values, ,
    #: received from the bdss. Each value can be of any type. The order of
    #: the parameters in each evaluation step must match the order of
    #: value_names
    evaluation_steps = List(List(Any))

    #: Selected step, used for highlighting in the table/plot
    selected_step_index = Int(None)

    view = View(Tabbed(
        VGroup(
            Spring(),
            label='Result Table'
        ),
        VGroup(
            Spring(),
            label='Pareto Front'
        )
    ))
