from traits.api import (
    Bool, Event, Instance, List, Unicode,
    on_trait_change, HasTraits
)
from traitsui.api import (ModelView
)

from force_bdss.api import KPISpecification, BaseMCOModel
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)


class MCOOptionsView(HasTraits):
    """A Base class for MCOParameterView and KPISpecificationView classes"""
    # -------------------
    # Required Attributes
    # -------------------

    #: MCO model (More restrictive than the ModelView model attribute)
    model = Instance(BaseMCOModel)

    #: Registry of the available variables
    variable_names_registry = Instance(VariableNamesRegistry)

    # ------------------
    # Regular Attributes
    # ------------------

    #: List of kpi ModelViews to display in ListEditor notebook
    model_views = List(Instance(ModelView))

    # ------------------
    # Dependent Attributes
    # ------------------

    #: The selected KPI in kpi_model_views
    selected_model_view = Instance(ModelView)

    #: Defines if the KPI is valid or not. Set by the function
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    valid = Bool(True)

    #: An error message for issues in this modelview. Set by the function
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    error_message = Unicode()

    #: Event to request a verification check on the workflow
    #: Listens to: `model.name`,`model.objective`
    verify_workflow_event = Event()

    # ------------------
    #     Properties
    # ------------------


    def __init__(self, model=None, *args, **kwargs):
        super(MCOOptionsView, self).__init__(*args, **kwargs)
        if model is not None:
            self.model = model

    # Defaults
    def _selected_model_view_default(self):
        """Default selected_kpi is the first in the list"""
        if len(self.selected_model_view) > 0:
            return self.selected_model_view[0]

    # Workflow Validation
    @on_trait_change('model_views.verify_workflow_event')
    def received_verify_request(self):
        """Pass on call for verify_workflow_event"""
        self.verify_workflow_event = True
