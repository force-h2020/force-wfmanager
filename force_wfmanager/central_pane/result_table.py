from traits.api import (
    Either, HasStrictTraits, Instance, List, Property, Tuple, on_trait_change
)
from traitsui.api import TabularEditor, UItem, View
from traitsui.tabular_adapter import TabularAdapter
from traitsui.table_column import ListColumn

from .analysis_model import AnalysisModel


class ResultTable(HasStrictTraits):
    # -------------------
    # Required Attributes
    # -------------------

    #: The model for the result table
    analysis_model = Instance(AnalysisModel)

    #: Adapter initialised with dummy columns to circumvent
    #: issues raised when setting up the View with no columns
    tabular_adapter = Instance(TabularAdapter, ())

    # --------------------
    # Dependent Attributes
    # --------------------

    #: Selected evaluation steps in the table
    _selected_rows = Either(List(Tuple), None)

    # ----------
    # Properties
    # ----------

    #: Rows of the table_editor
    rows = Property(
        List(Tuple), depends_on='analysis_model.evaluation_steps'
    )

    #: Columns of the table_editor
    columns = Property(
        List(ListColumn), depends_on='analysis_model.value_names'
    )

    def _get_rows(self):
        return self.analysis_model.evaluation_steps

    def _get_columns(self):
        return [ListColumn(label=name, index=index)
                for index, name
                in enumerate(self.analysis_model.value_names)]

    # ----
    # View
    # ----
    def default_traits_view(self):
        editor = TabularEditor(adapter=self.tabular_adapter,
                               show_titles=True,
                               auto_update=False,
                               editable=False)

        return View(UItem("rows", editor=editor))

    # Response to model initialisation
    @on_trait_change('analysis_model.value_names')
    def _update_adapter(self):
        self.tabular_adapter.columns = (
            [name for name in self.analysis_model.value_names])
        self.tabular_adapter.format = '% 5.4E'

    # Response to model change
    @on_trait_change('analysis_model.selected_step_index')
    def update_table(self):
        """ Updates the selected row in the table according to the model """
        if self.analysis_model.selected_step_index is None:
            self._selected_rows = []
        else:
            self._selected_rows = [
                self.rows[self.analysis_model.selected_step_index]
            ]

    # Response to new selection by user in UI
    @on_trait_change('_selected_rows[]')
    def update_model(self):
        """ Updates the model according to the selected row in the table """
        if not self._selected_rows:
            self.analysis_model.selected_step_index = None
        else:
            self.analysis_model.selected_step_index = \
                self.analysis_model.evaluation_steps.index(
                    self._selected_rows[0])
