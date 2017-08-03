from pyface.tasks.api import TraitsTaskPane

from traitsui.api import View, Tabbed, VGroup, Spring


class Analysis(TraitsTaskPane):
    id = 'force_wfmanager.analysis'
    name = 'Analysis'

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
