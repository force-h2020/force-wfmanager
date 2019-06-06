from traits.api import (
    Bool, Enum, Event, Instance, List, Property, Unicode, cached_property,
    on_trait_change
)
from traitsui.api import EnumEditor, Item, ModelView, View

from force_bdss.api import KPISpecification, Identifier
from force_wfmanager.ui.variable_names_registry import (
    VariableNamesRegistry
)


class KPISpecificationModelView(ModelView):

    # -------------------
    # Required Attributes
    # -------------------

    #: KPI model
    model = Instance(KPISpecification, allow_none=False)

    #: Registry of the available variables
    variable_names_registry = Instance(VariableNamesRegistry)

    # ------------------
    # Regular Attributes
    # ------------------

    #: Defines if the KPI is valid or not. Set by the function
    #: verify_tree in workflow_tree.py
    valid = Bool(True)

    #: An error message for issues in this modelview. Set by the function
    #: verify_tree in workflow_tree.py
    error_message = Unicode()

    # ------------------
    # Derived Attributes
    # ------------------

    #: Event to request a verification check on the workflow
    #: Listens to: `model.name`,`model.objective`
    verify_workflow_event = Event

    #: The name of the selected KPI
    #: Listens to: `variable_names_registry.data_source_outputs`
    name = Enum(values='_combobox_values')

    #: Values for the combobox
    #: #: Listens to: `variable_names_registry.data_source_outputs`
    _combobox_values = List(Identifier)

    # ----------
    # Properties
    # ----------

    #: The human readable name of the KPI
    label = Property(depends_on='model.name,model.objective')

    # ----
    # View
    # ----

    #: Base view for the MCO parameter
    traits_view = View(
        Item('model.name', editor=EnumEditor(name='object._combobox_values')),
        Item("model.objective"),
        Item('model.auto_scale'),
        Item("model.scale_factor", visible_when='not model.auto_scale'),
        kind="subpanel",
    )

    def __init__(self, model, variable_names_registry, **kwargs):
        super(KPISpecificationModelView, self).__init__(
            model=model,
            variable_names_registry=variable_names_registry,
            **kwargs
        )

    @on_trait_change('model.name,model.objective')
    def kpi_change(self):
        self.verify_workflow_event = True

    @on_trait_change('variable_names_registry.data_source_outputs')
    def update_combobox_values(self):
        available = self.variable_names_registry.data_source_outputs
        self._combobox_values = [''] + available

        self.name = ('' if self.name not in available else self.name)

        # If the KPI choice is no longer valid, change the model as well as
        # the view. This does not happen automatically when model.name is
        # set to a value not in _combobox_values
        if self.model is not None and self.name == '':
            self.model.name = ''

    @on_trait_change('model.name')
    def update_name(self):
        if self.model is None:
            self.name = ''
        else:
            self.name = self.model.name

    @cached_property
    def _get_label(self):
        """Gets the label from the model object"""
        if self.model.name == '':
            return "KPI"
        elif self.model.objective == '':
            return "KPI: {}".format(self.model.name)

        return "KPI: {} ({})".format(self.model.name, self.model.objective)
