from traits.api import (
    Instance, Unicode, Bool, on_trait_change, Event, Property,
    cached_property, List
)
from traitsui.api import (
    View, Item, ModelView, InstanceEditor,
    EnumEditor
)

from force_bdss.api import BaseMCOParameter

from force_wfmanager.ui.ui_utils import get_factory_name


class MCOParameterModelView(ModelView):

    # -------------------
    # Required Attributes
    # -------------------

    #: MCO parameter model
    model = Instance(BaseMCOParameter)

    #: Only display name options for existing Parameters
    # FIXME: this isn't an ideal method, since it requires further
    # work arounds for the name validation. Putting better error
    # handling into the force_bdss could resolve this.
    _combobox_values = List(Unicode)

    # ------------------
    # Dependent Attributes
    # ------------------

    #: Defines if the MCO parameter is valid or not. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    valid = Bool(True)

    #: An error message for issues in this modelview. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    error_message = Unicode()

    #: Event to request a verification check on the workflow
    #: Listens to: :attr:`model.name <model>` and :attr:`model.type <model>`
    verify_workflow_event = Event

    # ----------
    # Properties
    # ----------

    #: The human readable name of the MCO parameter class
    label = Property(Unicode(), depends_on="model.[name,type]")

    # ----------
    #    View
    # ----------

    def default_traits_view(self):
        """Default view containing both traits from the base class and
        any additional user-defined traits"""

        return View(Item('name', object='model',
                         editor=EnumEditor(name='object._combobox_values')),
                    Item('type', object='model'),
                    Item('model',
                         editor=InstanceEditor(),
                         style='custom')
                    )

    #: Defaults
    def _label_default(self):
        """Return a default label corresponding to the MCO parameter factory"""
        return get_factory_name(self.model.factory)

    #: Property getters
    @cached_property
    def _get_label(self):
        """Return a label appending both the parameter name and type to the
        default"""
        if self.model.name == '' and self.model.type == '':
            return self._label_default()
        return self._label_default()+': {type} {name}'.format(
            type=self.model.type, name=self.model.name
        )

    #: Listeners
    # Workflow Validation
    @on_trait_change('model.[name,type]')
    def parameter_change(self):
        """Alert to a change in the model"""
        self.verify_workflow_event = True

    @on_trait_change('model.name,_combobox_values')
    def _check_parameter_name(self):
        """Check the model name against all possible input variable
        names. Clear the model name if a matching output is not found"""
        if self.model is not None:
            if self._combobox_values is not None:
                if self.model.name not in self._combobox_values + ['']:
                    self.model.name = ''
