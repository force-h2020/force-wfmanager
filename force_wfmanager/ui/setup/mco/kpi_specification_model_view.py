from traits.api import (
    Bool, Event, Instance, List, Property, Unicode,
    on_trait_change
)
from traitsui.api import (
    Item, View, ModelView, EnumEditor
)

from force_bdss.api import KPISpecification


class KPISpecificationModelView(ModelView):

    # -------------------
    # Required Attributes
    # -------------------

    #: KPI model
    model = Instance(KPISpecification)

    #: Only display name options for existing KPIs
    # FIXME: this isn't an ideal method, since it requires further
    # work arounds for the name validation. Putting better error
    # handling into the force_bdss could resolve this.
    _combobox_values = List(Unicode)

    # ------------------
    # Regular Attributes
    # ------------------

    #: Defines if the KPI is valid or not. Set by the function
    #: map_verify_workflow in workflow_view.py
    valid = Bool(True)

    #: An error message for issues in this modelview. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    error_message = Unicode()

    #: Event to request a verification check on the workflow
    #: Listens to: :attr:`model.name <model>` and :attr:`model.type <model>`
    verify_workflow_event = Event

    # ------------------
    #     Properties
    # ------------------

    #: Human readable label for ModelView
    label = Property(Instance(Unicode),
                     depends_on='model:[name,objective]')

    # ------------------
    #     View
    # ------------------

    # The traits_view only displays possible options for
    # model.name listed in kpi_names. However, it is possible
    # to directly change model.name without updating kpi_names
    traits_view = View(
        Item('name', object='model',
             editor=EnumEditor(name='object._combobox_values')),
        Item("objective", object='model'),
        Item('auto_scale', object='model'),
        Item("scale_factor", object='model',
             visible_when='not model.auto_scale'),
        kind="subpanel",
    )

    #: Property getters
    def _get_label(self):
        """Gets the label from the model object"""
        if self.model.name == '':
            return "KPI"
        return "KPI: {} ({})".format(self.model.name, self.model.objective)

    #: Listeners
    @on_trait_change('model.[name,objective]')
    def kpi_change(self):
        """Raise verfiy workflow event upon change in model"""
        self.verify_workflow_event = True

    @on_trait_change('model.name,_combobox_values')
    def _check_kpi_name(self):
        """Check the model name against all possible output variable
        names. Clear the model name if a matching output is not found"""
        if self.model is not None:
            if self._combobox_values is not None:
                if self.model.name not in self._combobox_values + ['']:
                    self.model.name = ''

