from traits.api import (HasStrictTraits, List, Instance, Property, Tuple,
                        on_trait_change, Either)

from traitsui.api import View, UItem, TableEditor
from traitsui.table_column import ListColumn

from .analysis_model import AnalysisModel


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

    #: Selected cells indices in the table
    selected_indices = Either(List(Tuple), None)

    view = View(
        UItem("rows", editor=TableEditor(
            sortable=False,
            configurable=False,
            columns_name='columns',
            selection_mode='row',
            selected_indices='selected_indices',
        ))
    )

    def _get_rows(self):
        return self.analysis_model.evaluation_steps

    def _get_columns(self):
        return [ListColumn(label=name, index=index)
                for index, name
                in enumerate(self.analysis_model.value_names)]

    @on_trait_change('selected_indices')
    def update_selected(self):
        if self.selected_indices is None:
            self.analysis_model.selected_step_index = self.selected_indices
        else:
            self.analysis_model.selected_step_index = \
                self.selected_indices[0][0]
