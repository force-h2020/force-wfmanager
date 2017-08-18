from traits.api import HasStrictTraits, List, Instance, on_trait_change

from force_bdss.api import Identifier

from .mco_parameter_model_view import MCOParameterModelView
from .data_source_model_view import DataSourceModelView
from kpi_calculator_model_view import KPICalculatorModelView


class VariableNamesRegister(HasStrictTraits):
    #: MCO parameters model views
    mco_parameters_mv = List(Instance(MCOParameterModelView))

    #: MCO parameters names
    mco_parameters_names = List(Identifier)

    #: Data sources model views
    data_sources_mv = List(Instance(DataSourceModelView))

    #: Data sources output names
    data_sources_output_names = List(Identifier)

    #: KPI Calculators model views
    kpi_calculators_mv = List(Instance(KPICalculatorModelView))

    def _mco_parameters_names_default(self):
        return []

    def _data_sources_output_names_default(self):
        return []

    @on_trait_change('mco_parameters_mv.model.name')
    def update_mco_parameters_names(self):
        self.mco_parameters_names = [
            p.model.name
            for p in self.mco_parameters_mv
            if len(p.model.name) != 0
        ]

    @on_trait_change('data_sources_mv.model.output_slot_names[]')
    def update_data_sources_output_names(self):
        data_sources_output_names = []

        for data_source_mv in self.data_sources_mv:
            data_sources_output_names.extend(
                data_source_mv.model.output_slot_names)

        # Removes empty strings from the variable names
        while '' in data_sources_output_names:
            data_sources_output_names.pop(data_sources_output_names.index(''))

        self.data_sources_output_names = data_sources_output_names

    @on_trait_change('mco_parameters_names')
    def update_data_sources_inputs(self):
        for data_source_mv in self.data_sources_mv:
            data_source_mv.available_variables = self.mco_parameters_names

    @on_trait_change('mco_parameters_names,data_sources_output_names')
    def update_kpi_calculators_inputs(self):
        for kpi_calculator_mv in self.kpi_calculators_mv:
            kpi_calculator_mv.available_variables = \
                self.mco_parameters_names + self.data_sources_output_names
