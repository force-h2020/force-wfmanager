from traits.api import List, Instance, Int, Any, Str, HasStrictTraits, Bool

from traitsui.api import View, Item, TableEditor
from traitsui.table_column import ObjectColumn


class Result(HasStrictTraits):
    name = Str()
    value = Any()


class EvaluationStep(HasStrictTraits):
    _step = 0

    @staticmethod
    def init_step_count():
        EvaluationStep._step = 0

    step = Int()
    results = List(Instance(Result))

    def _step_default(self):
        EvaluationStep._step += 1
        return EvaluationStep._step


class ResultColumn(ObjectColumn):
    editable = Bool(False)

    def get_value(self, object):
        for result in object.results:
            if result.name == self.name:
                return str(result.value)
        return None


table_editor = TableEditor(
    sortable=False,
    configurable=False,
    auto_size=False,
    selected_indices='selected_step_indices',
    columns_name='columns'
)


class ResultTable(HasStrictTraits):
    #: Each row of the table containing the evaluation step
    evaluation_steps = List(Instance(EvaluationStep))

    #: The currently selected indices in the table
    selected_step_indices = List(Int)

    #: The column labels (result names)
    column_names = List(Str)

    #: The columns
    columns = List(Instance(ObjectColumn))

    traits_view = View(
        Item('evaluation_steps', editor=table_editor)
    )

    def append_evaluation_step(self, evaluation_step):
        """ Appends an evalutation step to the table, it automatically adds a
        new column if needed (e.g. if there is no column 'x' but the
        evalutation step a result named 'x', a new column will be created) """
        result_names = [result.name for result in evaluation_step.results]
        for name in result_names:
            if name not in self.column_names:
                self.add_column(name)
        self.evaluation_steps.append(evaluation_step)

    def add_column(self, name):
        """ Creates a new column in the table """
        self.column_names.append(name)
        self.columns.append(ResultColumn(name=name))

    def clear_table(self):
        self.evaluation_steps = []
        self.column_names = self._column_names_default()
        self.columns = self._columns_default()
        EvaluationStep.init_step_count()

    def _column_names_default(self):
        return ['step']

    def _columns_default(self):
        return [ObjectColumn(name='step')]
