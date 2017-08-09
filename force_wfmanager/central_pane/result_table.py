from traits.api import HasStrictTraits, List, Instance, Property, Tuple

from traitsui.api import View, UItem, TableEditor
from traitsui.table_column import ListColumn

from .analysis_model import AnalysisModel


table_editor = TableEditor(
    sortable=False,
    configurable=False,
    auto_size=False,
    columns_name='columns'
)


class ResultTable(HasStrictTraits):
    #: The model for the result table
    analysis_model = Instance(AnalysisModel)

    #: Rows of the table_editor
    rows = Property(
        List(Tuple),
        depends_on='analysis_model.evaluation_steps'
    )

    #: Columns of the table_editor
    columns = Property(
        List(ListColumn),
        depends_on='analysis_model.value_names'
    )

    view = View(
        UItem("rows", editor=table_editor)
    )

    def _get_rows(self):
        return self.analysis_model.evaluation_steps

    def _get_columns(self):
        return [ListColumn(label=name, index=index)
                for index, name
                in enumerate(self.analysis_model.value_names)]
