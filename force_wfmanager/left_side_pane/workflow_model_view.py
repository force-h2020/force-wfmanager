from traits.api import Instance, List, Property
from traitsui.api import ModelView

from force_bdss.core.workflow import Workflow
from force_bdss.api import (BaseMCOModel, BaseMCOParameter,
                            BaseDataSourceModel, BaseKPICalculatorModel)

from .mco_model_view import MCOModelView
from .data_source_model_view import DataSourceModelView
from .kpi_calculator_model_view import KPICalculatorModelView


class WorkflowModelView(ModelView):
    #: Workflow model
    model = Instance(Workflow, allow_none=False)

    #: List of MCO to be displayed in the TreeEditor
    mco_representation = Property(
        List(Instance(MCOModelView)),
        depends_on='model.mco')

    #: List of DataSources to be displayed in the TreeEditor
    data_sources_representation = Property(
        List(Instance(DataSourceModelView)),
        depends_on='model.data_sources')

    #: List of KPI Calculators to be displayed in the TreeEditor
    kpi_calculators_representation = Property(
        List(Instance(KPICalculatorModelView)),
        depends_on='model.kpi_calculators')

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
            If no MCO is defined for the Workflow
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

    def _get_mco_representation(self):
        if self.model.mco is not None:
            return [MCOModelView(model=self.model.mco)]
        else:
            return []

    def _get_data_sources_representation(self):
        return [DataSourceModelView(model=data_source)
                for data_source in self.model.data_sources]

    def _get_kpi_calculators_representation(self):
        return [KPICalculatorModelView(model=kpi_calculator)
                for kpi_calculator in self.model.kpi_calculators]

    def _model_default(self):
        return Workflow()
