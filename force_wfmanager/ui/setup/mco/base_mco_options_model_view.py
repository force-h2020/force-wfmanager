from traits.api import (
    Bool, Event, Instance, List, Property, Unicode,
    on_trait_change, Either, Tuple
)
from traitsui.api import (
    ModelView
)

from force_bdss.api import (
    KPISpecification, BaseMCOParameter, Identifier
)
from force_bdss.local_traits import CUBAType


class BaseMCOOptionsModelView(ModelView):

    # -------------------
    # Required Attributes
    # -------------------

    #: KPI model
    model = Either(Instance(KPISpecification),
                   Instance(BaseMCOParameter))

    #: Only display name and type options for available variables
    # FIXME: this isn't an ideal method, since it requires further
    # work arounds for the name validation. Putting better error
    # handling into the force_bdss could resolve this.
    available_variables = List(Tuple(Identifier, CUBAType))

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

    #: Values for model.name EnumEditor in traits_view
    _combobox_values = Property(List(Identifier),
                                depends_on='available_variables')

    def __init__(self, model=None, *args, **kwargs):
        super(BaseMCOOptionsModelView, self).__init__(*args, **kwargs)
        if model is not None:
            self.model = model

    # ------------------
    #     Listeners
    # ------------------

    def _get__combobox_values(self):
        """Update combobox_values based on available variable names"""
        _combobox_values = []
        if self.available_variables is not None:
            for variable in self.available_variables:
                _combobox_values.append(variable[0])

        return _combobox_values

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
