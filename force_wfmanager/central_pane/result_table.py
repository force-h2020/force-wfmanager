from traits.api import HasStrictTraits, List, Str, Tuple, Property

from traitsui.api import View, UItem, TableEditor
from traitsui.table_column import ListColumn


table_editor = TableEditor(
    sortable=False,
    configurable=False,
    auto_size=False,
    columns_name='columns'
)


class ResultTable(HasStrictTraits):
    #: List of parameter names
    value_names = List(Str)

    #: List of evaluation steps
    evaluation_steps = List(Tuple())

    #: Columns of the table_editor
    columns = Property(
        List(ListColumn),
        depends_on='value_names'
    )

    view = View(
        UItem(name='evaluation_steps', editor=table_editor)
    )

    def _get_columns(self):
        return [ListColumn(label=name, index=index)
                for index, name
                in enumerate(self.value_names)]
