from pyface.tasks.api import TraitsTaskPane

from traits.api import Instance, Int

from traitsui.api import View, Tabbed, VGroup, Item

from .result_table import ResultTable, EvaluationStep, Result


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
        ev1 = EvaluationStep(results=[
            Result(name="x", value="0.1"),
            Result(name="y", value="0.2"),
            Result(name="z", value="0.123"),
            Result(name="n", value="36"),
        ])
        ev2 = EvaluationStep(results=[
            Result(name="x", value="32"),
            Result(name="y", value="2"),
            Result(name="z", value="23"),
            Result(name="n", value="56"),
        ])
        table = ResultTable()
        table.append_evaluation_step(ev1)
        table.append_evaluation_step(ev2)
        return table
