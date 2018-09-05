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

    #: Selected evaluation steps in the table
    _selected_rows = Either(List(Tuple), None)

    view = View(
        UItem("rows", editor=TableEditor(
            sortable=False,
            configurable=False,
            columns_name='columns',
            # Using rows instead of row because of a traitsui bug
            selection_mode='rows',
            selected='_selected_rows',
        ))
    )

    def _get_rows(self):
        return self.analysis_model.evaluation_steps

    def _get_columns(self):
        return [ListColumn(label=name, index=index)
                for index, name
                in enumerate(self.analysis_model.value_names)]

    @on_trait_change('analysis_model.selected_step_index')
    def update_table(self):
        """ Updates the selected row in the table according to the model """
        if self.analysis_model.selected_step_index is None:
            self._selected_rows = []
        else:
            self._selected_rows = \
                [self.rows[self.analysis_model.selected_step_index]]

    @on_trait_change('_selected_rows[]')
    def update_model(self):
        """ Updates the model according to the selected row in the table """
        if len(self._selected_rows) == 0:
            self.analysis_model.selected_step_index = None
        else:
            self.analysis_model.selected_step_index = \
                self.analysis_model.evaluation_steps.index(
                    self._selected_rows[0])
