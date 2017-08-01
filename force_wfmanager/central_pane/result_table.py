from traits.api import List, Instance, Int, Any, Str, HasStrictTraits, Bool

from traitsui.api import View, Item, TableEditor
from traitsui.table_column import ObjectColumn


class Result(HasStrictTraits):
    name = Str()
    value = Any()


class EvaluationStep(HasStrictTraits):
    _step = 0

    @staticmethod
    def _get_step(cls):
        cls._step += 1
        return cls._step

    @staticmethod
    def init_step_count(cls):
        cls._step = 0

    step = Int()
    results = List(Instance(Result))

    def _step_default(self):
        return self._get_step(EvaluationStep)


class ResultColumn(ObjectColumn):
    editable = Bool(False)

    def get_value(self, object):
        for result in object.results:
            if result.name == self.name:
                return result.value
        return None


table_editor = TableEditor(
    sortable=False,
    configurable=False,
    auto_size=False,
    selected_indices='selected_step_indices',
    columns_name='columns'
)


class ResultTable(HasStrictTraits):
    #: Each row of the table containing the results
    evaluation_steps = List(Instance(EvaluationStep))

    #: The currently selected indices in the table
    selected_step_indices = List(Int)

    #: The column labels
    column_names = List(Str)

    #: The column objects
    columns = List(Instance(ResultColumn))

    traits_view = View(
        Item('evaluation_steps', editor=table_editor)
    )

    def append_evaluation_step(self, evaluation_step):
        result_names = [result.name for result in evaluation_step.results]
        for name in result_names:
            if name not in self.column_names:
                self.add_column(name)
        self.evaluation_steps.append(evaluation_step)

    def add_column(self, name):
        self.column_names.append(name)
        self.columns.append(ResultColumn(name=name))
