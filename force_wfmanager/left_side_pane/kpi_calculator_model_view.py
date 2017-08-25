from traits.api import Instance, on_trait_change

from force_bdss.api import BaseKPICalculatorModel

from .evaluator_model_view import EvaluatorModelView


class KPICalculatorModelView(EvaluatorModelView):
    #: KPI Calculator model (More restrictive than the ModelView model
    #: attribute)
    model = Instance(BaseKPICalculatorModel, allow_none=False)

    def __evaluator_default(self):
        return self.model.factory.create_kpi_calculator()

    @on_trait_change(
        'variable_names_registry.kpi_calculator_available_variables[]')
    def update_kpi_calculator_input_rows(self):
        available_variables = self._get_available_variables()
        for input_slot_row in self.input_slots_representation:
            input_slot_row.available_variables = available_variables

    def _get_available_variables(self):
        return self.variable_names_registry.kpi_calculator_available_variables
