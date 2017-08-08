from traits.api import HasStrictTraits, List, Instance, Property

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

    #: Columns of the table_editor
    columns = Property(
        List(ListColumn),
        depends_on='analysis_model.value_names'
    )

    view = View(
        UItem("analysis_model.evaluation_steps", editor=table_editor)
    )

    def _get_columns(self):
        return [ListColumn(label=name, index=index)
                for index, name
                in enumerate(self.analysis_model.value_names)]
