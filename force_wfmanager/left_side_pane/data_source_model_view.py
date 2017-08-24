from traits.api import Instance, on_trait_change

from force_bdss.api import BaseDataSourceModel

from .evaluator_model_view import EvaluatorModelView


class DataSourceModelView(EvaluatorModelView):
    #: DataSource model (More restrictive than the ModelView model attribute)
    model = Instance(BaseDataSourceModel, allow_none=False)

    def __evaluator_default(self):
        return self.model.factory.create_data_source()

    @on_trait_change(
        'variable_names_registry.data_source_available_variables[]')
    def update_data_source_input_rows(self):
        available_variables = self._get_available_variables()
        for input_slot_row in self.input_slots_representation:
            input_slot_row.available_variables = available_variables

    def _get_available_variables(self):
        return self.variable_names_registry.data_source_available_variables
