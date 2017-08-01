from pyface.tasks.api import TraitsTaskPane

from traits.api import Int

from traitsui.api import View, Tabbed, VGroup, Item


class Analysis(TraitsTaskPane):
    id = 'force_wfmanager.analysis'
    name = 'Analysis'

    test1 = Int()
    test2 = Int()

    view = View(Tabbed(
        VGroup(
            Item('test1'),
            label='Pareto Front'
        ),
        VGroup(
            Item('test2'),
            label='Results'
        )
    ))
