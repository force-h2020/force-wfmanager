from traits.api import (
    Bool, Enum, Event, Instance, List, Property, Unicode, cached_property,
    on_trait_change, HasTraits
)
from traitsui.api import EnumEditor, Item, View

from force_bdss.api import KPISpecification, Identifier
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)


class KPISpecificationView(HasTraits):

    # -------------------
    # Required Attributes
    # -------------------

    #: KPI model
    model = Instance(KPISpecification)

    #: Registry of the available variables, defines the
    #: output variables able to be optimised as KPIs
    variable_names_registry = Instance(VariableNamesRegistry)

    # ------------------
    # Regular Attributes
    # ------------------

    #: Defines if the KPI is valid or not. Set by the function
    #: map_verify_workflow in process_tree.py
    valid = Bool(True)

    #: An error message for issues in this modelview. Set by the function
    #: verify_tree in process_tree.py
    error_message = Unicode()

    # ------------------
    # Derived Attributes
    # ------------------

    #: Event to request a verification check on the workflow
    #: Listens to: `model.name`,`model.objective`
    verify_workflow_event = Event

    #: The name of the selected KPI
    #: Depends on list of strings in `_combobox_values`
    name = Enum(values='_combobox_values')

    #: Values for the combobox
    #: Listens to: `variable_names_registry.data_source_outputs`
    _combobox_values = Property(
        List(Identifier),
        depends_on='variable_names_registry.data_source_outputs'
    )

    # ----------
    # Properties
    # ----------

    #: The human readable name of the KPI
    label = Property(depends_on='model.[name,objective]')

    def __init__(self, model=None, *args, **kwargs):
        super(KPISpecificationView, self).__init__(*args, **kwargs)
        if model is not None:
            self.model = model

    def default_traits_view(self):
        #: Base view for the MCO parameter
        traits_view = View(
            Item('model.name', editor=EnumEditor(name='object._combobox_values')),
            Item("model.objective"),
            Item('model.auto_scale'),
            Item("model.scale_factor", visible_when='not model.auto_scale'),
            kind="subpanel",
        )

        return traits_view

    @on_trait_change('_combobox_values')
    def check_kpi_name(self):
        #: Clear the existing name if it is not allowed upon update of
        #: the combobox
        if self.model is not None:
            if self.model.name not in self._combobox_values:
                # Propagate the name change to the model - note: this does
                # not happen automatically when model.name is set to a
                # value not in _combobox_values
                self.model.name = ''

    @on_trait_change('model.[name,objective]')
    def kpi_change(self):
        self.verify_workflow_event = True

    @on_trait_change('model.name')
    def update_name(self):
        #: Check if model has been removed
        print('kpi_view update_name called')
        if self.model is None:
            self.name = ''
        else:
            self.name = self.model.name

    @cached_property
    def _get__combobox_values(self):
        print('kpi_view _get__combobox_values called')
        if self.variable_names_registry is not None:
            available = self.variable_names_registry.data_source_outputs
            return [''] + available
        else:
            return ['']

    @cached_property
    def _get_label(self):
        """Gets the label from the model object"""
        print('kpi_view _get_label called')
        if self.model.name == '':
            return "KPI"
        elif self.model.objective == '':
            return "KPI: {}".format(self.model.name)

        return "KPI: {} ({})".format(self.model.name, self.model.objective)
