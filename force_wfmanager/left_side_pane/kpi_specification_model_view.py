from traits.api import Instance, Str, Bool, Enum, List, on_trait_change
from traitsui.api import ModelView, View, Item

from force_bdss.core.kpi_specification import KPISpecification
from force_bdss.local_traits import Identifier
from force_wfmanager.left_side_pane.variable_names_registry import \
    VariableNamesRegistry


class KPISpecificationModelView(ModelView):
    #: KPI model
    model = Instance(KPISpecification, allow_none=False)

    #: Registry of the available variables
    variable_names_registry = Instance(VariableNamesRegistry)

    #: The human readable name of the KPI
    label = Str()

    #: Defines if the KPI is valid or not
    valid = Bool(True)

    name = Enum(values='_combobox_values')

    available_variables = List(Identifier)

    _combobox_values = List(Identifier)

    #: Base view for the MCO parameter
    traits_view = View(
        Item("name"),
        Item("model.objective"),
        kind="subpanel",
    )

    def _label_default(self):
        return _get_label(self.model)

    @on_trait_change('variable_names_registry.available_variables[]')
    def update_combobox_values(self):
        available = self.variable_names_registry.available_variables[-1]
        self._combobox_values = [''] + available
        self.name = ('' if self.name not in available else self.name)


def _get_label(model):
    """Gets the label from the model object"""
    if model.name == '':
        return "KPI"

    return "KPI: {}".format(model.name)
