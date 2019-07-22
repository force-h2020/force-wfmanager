from traits.api import (
    Bool, Event, Instance, List, Property, Unicode,
    on_trait_change, Either
)
from traitsui.api import (
    ModelView
)

from force_bdss.api import KPISpecification, BaseMCOParameter


class BaseMCOOptionsModelView(ModelView):

    # -------------------
    # Required Attributes
    # -------------------

    #: KPI model
    model = Either(Instance(KPISpecification),
                   Instance(BaseMCOParameter))

    #: Only display name options for existing MCO Parameters and KPIs
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
    label = Instance(Property)

    #: Property getters
    def _get_label(self):
        """Needs to be implemented by child class"""
        raise NotImplementedError(
            "_get_label was not implemented in {}".format(
                self.__class__))

    #: Listeners
    # Assign an on_trait_change decorator to specify traits to listen to
    # in child class implementation
    def model_change(self):
        """Raise verify workflow event upon change in model"""
        self.verify_workflow_event = True

    @on_trait_change('model.name,_combobox_values')
    def _check_model_name(self):
        """Check the model name against all possible output variable
        names. Clear the model name if a matching output is not found"""
        if self.model is not None:
            if self._combobox_values is not None:
                if self.model.name not in self._combobox_values + ['']:
                    self.model.name = ''
