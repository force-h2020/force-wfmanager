from traits.api import (
    Bool, Event, Instance, List, Unicode, Either, on_trait_change
)
from traitsui.api import (
    ModelView
)

from force_bdss.api import (
    KPISpecification, BaseMCOParameter
)
from force_wfmanager.utils.variable_names_registry import (
    Variable
)


class BaseMCOOptionsModelView(ModelView):

    # -------------------
    # Required Attributes
    # -------------------

    #: Either a MCO KPI or parameter model
    model = Either(Instance(KPISpecification),
                   Instance(BaseMCOParameter))

    # Variable selected by the UI to hook model up to
    selected_variable = Instance(Variable)

    #: List of available variables for UI selection
    available_variables = List(Variable)

    # ------------------
    # Regular Attributes
    # ------------------

    #: Defines if the KPI/parameter is valid or not. Updated by
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

    # ------------------
    #     Properties
    # ------------------

    def __init__(self, model=None, *args, **kwargs):
        super(BaseMCOOptionsModelView, self).__init__(*args, **kwargs)
        if model is not None:
            self.model = model

    # ------------------
    #     Listeners
    # ------------------
    @on_trait_change('selected_variable,available_variables')
    def _check_available_variables(self):

        if self.selected_variable is not None:
            if self.selected_variable not in self.available_variables:
                self.selected_variable = None

    @on_trait_change('selected_variable')
    def _check_selected_model(self):

        if self.selected_variable is None:
            if self.model is not None:
                self.model.name = ''
                if isinstance(self.model, BaseMCOParameter):
                    self.model.type = ''

    # Assign an on_trait_change decorator to specify traits to listen to
    # in child class implementation
    def model_change(self):
        """Raise verify workflow event upon change in model"""
        self.verify_workflow_event = True
