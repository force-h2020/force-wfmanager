from pyface.tasks.api import TraitsTaskPane

from traits.api import Instance, Int

from traitsui.api import View, Tabbed, VGroup, Item

from .result_table import ResultTable


class Analysis(TraitsTaskPane):
    id = 'force_wfmanager.analysis'
    name = 'Analysis'

    result_table = Instance(ResultTable)

    test = Int()

    view = View(Tabbed(
        VGroup(
            Item('result_table', style='custom'),
            label='Results'
        ),
        VGroup(
            Item('test'),
            label='Pareto Front'
        )
    ))

    def _result_table_default(self):
        return ResultTable()
