from traits.api import Instance, List, on_trait_change
from traitsui.api import ModelView

from force_bdss.core.workflow import Workflow
from force_bdss.api import (BaseMCOModel, BaseMCOParameter,
                            BaseDataSourceModel, BaseKPICalculatorModel)

from .mco_model_view import MCOModelView
from .data_source_model_view import DataSourceModelView
from .kpi_calculator_model_view import KPICalculatorModelView
from .variable_names_register import VariableNamesRegister


class WorkflowModelView(ModelView):
    #: Workflow model
    model = Instance(Workflow, allow_none=False)

    #: List of MCO to be displayed in the TreeEditor
    mco_representation = List(Instance(MCOModelView))

    #: List of DataSources to be displayed in the TreeEditor
    data_sources_representation = List(Instance(DataSourceModelView))

    #: List of KPI Calculators to be displayed in the TreeEditor
    kpi_calculators_representation = List(Instance(KPICalculatorModelView))

    #: Variable Names Register
    variable_names_register = Instance(VariableNamesRegister)

    def __init__(self, model, *args, **kwargs):
        self.model = model

        super(WorkflowModelView, self).__init__(*args, **kwargs)

        mco_parameters_mv = [
            mco_mv.mco_parameters_representation
            for mco_mv in self.mco_representation
        ]
        self.variable_names_register = VariableNamesRegister(
            mco_parameters_mv=mco_parameters_mv
        )
        self.variable_names_register.data_sources_mv = \
            self.data_sources_representation
        self.variable_names_register.kpi_calculators_mv = \
            self.kpi_calculators_representation

        # Now that the variable names register is correctly set, we can update
        # the model views
        self.update_mco_representation()
        self.update_data_sources_representation()
        self.update_kpi_calculators_representation()

    def add_entity(self, entity):
        """ Adds an element to the workflow

        Parameters
        ----------
        entity: BaseMCOModel or BaseMCOParameter or BaseDataSourceModel or
            BaseKPICalculatorModel
            The element to be inserted in the Workflow

        Raises
        ------
        RuntimeError:
            If the entity is an MCO parameter but no MCO is defined for the
            Workflow.
        TypeError:
            If the type of the entity is not supported by the Workflow
        """
        if isinstance(entity, BaseMCOModel):
            self.model.mco = entity
        elif isinstance(entity, BaseMCOParameter):
            if self.model.mco is None:
                raise(RuntimeError("Cannot add a parameter to the "
                      "workflow if no MCO defined"))

            self.model.mco.parameters.append(entity)
        elif isinstance(entity, BaseDataSourceModel):
            self.model.data_sources.append(entity)
        elif isinstance(entity, BaseKPICalculatorModel):
            self.model.kpi_calculators.append(entity)
        else:
            raise(
                TypeError("Type {} is not supported by the workflow".format(
                    type(entity).__name__
                ))
            )

    def remove_entity(self, entity):
        """ Removes an element from the workflow

        Parameters
        ----------
        entity: BaseMCOModel or BaseMCOParameter or BaseDataSourceModel or
            BaseKPICalculatorModel
            The element to be removed from the Workflow

        Raises
        ------
        ValueError:
            If the element to be deleted is not present in the Workflow
        """
        if isinstance(entity, BaseMCOModel):
            if self.model.mco is entity:
                self.model.mco = None
            else:
                raise(
                    ValueError("The MCO {} can not be removed from the"
                               " workflow, it is not in the workflow".format(
                                   type(entity).__name__))
                )
        elif isinstance(entity, BaseMCOParameter):
            self.model.mco.parameters.remove(entity)
        elif isinstance(entity, BaseDataSourceModel):
            self.model.data_sources.remove(entity)
        elif isinstance(entity, BaseKPICalculatorModel):
            self.model.kpi_calculators.remove(entity)
        else:
            raise(
                ValueError("Element of type {} can not be removed from the"
                           " workflow".format(type(entity).__name__))
            )

    @on_trait_change('model.mco')
    def update_mco_representation(self):
        if self.model.mco is not None:
            self.mco_representation = [MCOModelView(model=self.model.mco)]
        else:
            self.mco_representation = []

    @on_trait_change('model.data_sources[]', post_init=True)
    def update_data_sources_representation(self):
        """ Update the data source model views """
        available_variables = self.variable_names_register.mco_parameters_names
        self.data_sources_representation = [
            DataSourceModelView(
                model=data_source,
                available_variables=available_variables
            )
            for data_source in self.model.data_sources]
        self.variable_names_register.data_sources_mv = \
            self.data_sources_representation

    @on_trait_change('model.kpi_calculators[]', post_init=True)
    def update_kpi_calculators_representation(self):
        """ Update the kpi calculator model views """
        available_variables = \
            self.variable_names_register.mco_parameters_names \
            + self.variable_names_register.data_sources_output_names
        self.kpi_calculators_representation = [
            KPICalculatorModelView(
                model=kpi_calculator,
                available_variables=available_variables
            )
            for kpi_calculator in self.model.kpi_calculators]
        self.variable_names_register.kpi_calculators_mv = \
            self.kpi_calculators_representation

    @on_trait_change('mco_representation.mco_parameters_representation[]')
    def update_variable_register(self):
        if len(self.mco_representation) != 0:
            self.variable_names_register.mco_parameters_mv = \
                self.mco_representation[0].mco_parameters_representation
        else:
            self.variable_names_register.mco_parameters_mv = []

    def _model_default(self):
        return Workflow()
