from traits.api import Instance, List, Property
from traitsui.api import ModelView

from force_bdss.workspecs.workflow import Workflow
from force_bdss.api import (BaseMCOModel, BaseMCOParameter,
                            BaseDataSourceModel, BaseKPICalculatorModel)

from .mco_model_view import MCOModelView


class WorkflowModelView(ModelView):
    #: Workflow model
    model = Instance(Workflow)

    #: List of MCO to be displayed in the TreeEditor
    mco_representation = Property(
        List(MCOModelView),
        depends_on='model.mco')

    #: List of DataSources to be displayed in the TreeEditor
    data_sources_representation = Property(
        List(BaseDataSourceModel),
        depends_on='model.data_sources')

    #: List of KPI Calculators to be displayed in the TreeEditor
    kpi_calculators_representation = Property(
        List(BaseKPICalculatorModel),
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

    def _get_mco_representation(self):
        if self.model.mco is not None:
            return [MCOModelView(model=self.model.mco)]
        else:
            return []

    def _get_data_sources_representation(self):
        return self.model.data_sources

    def _get_kpi_calculators_representation(self):
        return self.model.kpi_calculators

    def _model_default(self):
        return Workflow()
