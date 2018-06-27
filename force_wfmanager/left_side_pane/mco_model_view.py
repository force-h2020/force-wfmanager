from traits.api import Instance, List, Str, on_trait_change, Bool

from traitsui.api import ModelView

from force_bdss.api import BaseMCOModel
from force_wfmanager.left_side_pane.kpi_specification_model_view import \
    KPISpecificationModelView
from force_wfmanager.left_side_pane.variable_names_registry import \
    VariableNamesRegistry

from .mco_parameter_model_view import MCOParameterModelView
from .view_utils import get_factory_name


class MCOModelView(ModelView):
    #: MCO model (More restrictive than the ModelView model attribute)
    model = Instance(BaseMCOModel)

    #: Label to be used in the TreeEditor
    label = Str()

    #: List of MCO parameters to be displayed in the TreeEditor
    mco_parameters_mv = List(Instance(MCOParameterModelView))

    #: List of the KPISpecificationModelView to be displayed in the TreeEditor
    kpis_mv = List(Instance(KPISpecificationModelView))

    #: Registry of the available variables
    variable_names_registry = Instance(VariableNamesRegistry)

    #: Defines if the MCO is valid or not
    valid = Bool(True)

    error_message = Str

    def add_parameter(self, parameter):
        """Adds a parameter to the referred model."""
        self.model.parameters.append(parameter)

    def remove_parameter(self, parameter):
        """Removes a parameter from the referred model."""
        self.model.parameters.remove(parameter)

    def add_kpi(self, kpi):
        """Adds a KPISpecification to the underlying model"""
        self.model.kpis.append(kpi)

    def remove_kpi(self, kpi):
        """Removes a KPISpecification from the underlying model.
        """
        self.model.kpis.remove(kpi)

    @on_trait_change('model.parameters[]')
    def update_mco_parameters_mv(self):
        """ Update the MCOParameterModelViews """
        self.mco_parameters_mv = [
            MCOParameterModelView(model=parameter)
            for parameter in self.model.parameters]

    @on_trait_change('model.kpis[]')
    def update_kpis(self):
        """Updates the KPI modelview according to the new KPIs in the
        model"""
        self.kpis_mv = [
            KPISpecificationModelView(
                variable_names_registry=self.variable_names_registry,
                model=kpi
            )
            for kpi in self.model.kpis
        ]

    def _label_default(self):
        return get_factory_name(self.model.factory)
