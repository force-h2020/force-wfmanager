from traits.api import HasStrictTraits, List, Instance, on_trait_change

from force_bdss.api import Identifier
from force_bdss.core.workflow import Workflow


class VariableNamesRegistry(HasStrictTraits):
    """ Class used for listening to the structure of the Workflow in order to
    check the available variables that can be used as inputs for each layer
    (Datasources/KPICalculators) """
    # NOTE: For now there is only two layers, the DataSources layer and the KPI
    # Calculators layer. This is likely to change, we will have a list of
    # DataSources layers, then this class will need to be adapted and will
    # compute the available variables for each layer in the Workflow.

    #: Workflow model
    workflow = Instance(Workflow, allow_none=False)

    #: List of available variables for the data sources (MCO parameters names)
    data_source_available_variables = List(Identifier)

    #: List of available variables for the kpi calculators (Data sources output
    #: names and MCO parameters)
    kpi_calculator_available_variables = List(Identifier)

    #: List of MCO parameters
    _mco_parameters_names = List(Identifier)

    #: List of data sources outputs
    _data_sources_outputs = List(Identifier)

    @on_trait_change('workflow.mco.parameters.name')
    def update__mco_parameters_names(self):
        if self.workflow.mco is None:
            self._mco_parameters_names = []
            return

        self._mco_parameters_names = [
            p.name
            for p in self.workflow.mco.parameters
            if len(p.name) != 0
        ]

    @on_trait_change('workflow.data_sources.output_slot_names[]')
    def update__data_sources_outputs(self):
        data_sources_output_names = []

        for data_source in self.workflow.data_sources:
            data_sources_output_names.extend(data_source.output_slot_names)

        # Removes empty strings from the variable names
        while '' in data_sources_output_names:
            data_sources_output_names.pop(data_sources_output_names.index(''))

        self._data_sources_outputs = data_sources_output_names

    @on_trait_change('_mco_parameters_names')
    def update_available_variables(self):
        self.data_source_available_variables = self._mco_parameters_names
        self.update_kpi_calculators_available_variables()

    @on_trait_change('_data_sources_outputs')
    def update_kpi_calculators_available_variables(self):
        self.kpi_calculator_available_variables = \
            self._mco_parameters_names + self._data_sources_outputs
