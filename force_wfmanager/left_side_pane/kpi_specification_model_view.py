from traits.api import (Instance, Property, Bool, Enum, List, on_trait_change,
                        cached_property, Str, Event)
from traitsui.api import ModelView, View, Item, EnumEditor

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
    label = Property(depends_on='model.name')

    #: Defines if the KPI is valid or not
    valid = Bool(True)

    error_message = Str

    #: The name of the selected KPI
    name = Enum(values='_combobox_values')

    #: Values for the combobox
    _combobox_values = List(Identifier)

    #: Base view for the MCO parameter
    traits_view = View(
        Item('model.name', editor=EnumEditor(name='object._combobox_values')),
        Item("model.objective"),
        kind="subpanel",
    )

    #: Event to request a verification check on the workflow
    verify_workflow_event = Event

    def __init__(self, model, variable_names_registry, **kwargs):
        super(KPISpecificationModelView, self).__init__(
            model=model,
            variable_names_registry=variable_names_registry,
            **kwargs
        )

    @on_trait_change('model.name, model.objective')
    def kpi_change(self):
        self.verify_workflow_event = True

    @on_trait_change('variable_names_registry.data_source_outputs')
    def update_combobox_values(self):
        available = self.variable_names_registry.data_source_outputs
        self._combobox_values = [''] + available
        self.name = ('' if self.name not in available else self.name)

    @cached_property
    def _get_label(self):
        """Gets the label from the model object"""
        if self.model.name == '':
            return "KPI"

        return "KPI: {}".format(self.model.name)
