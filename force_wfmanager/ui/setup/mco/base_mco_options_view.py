from traits.api import (
    Bool, Event, Instance, List, Unicode,
    on_trait_change, HasTraits
)

from force_bdss.api import BaseMCOModel
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)
from force_wfmanager.ui.setup.mco.base_mco_options_model_view import (
    BaseMCOOptionsModelView
)


class BaseMCOOptionsView(HasTraits):
    """A Base class for MCOParameterView and KPISpecificationView
    classes"""

    # -------------------
    # Required Attributes
    # -------------------

    #: MCO model (More restrictive than the ModelView model attribute)
    model = Instance(BaseMCOModel)

    #: Registry of the available variables
    variable_names_registry = Instance(VariableNamesRegistry)

    # -----------------------
    #    Regular Attributes
    # -----------------------

    #: List of kpi ModelViews to display in ListEditor notebook
    model_views = List(Instance(BaseMCOOptionsModelView))

    # ------------------
    # Dependent Attributes
    # ------------------

    #: The selected option model_views
    selected_model_view = Instance(BaseMCOOptionsModelView)

    #: Defines if the MCOOption is valid or not. Set by the function
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

    def __init__(self, model=None, *args, **kwargs):
        super(BaseMCOOptionsView, self).__init__(*args, **kwargs)
        if model is not None:
            self.model = model

    # Defaults
    def _selected_model_view_default(self):
        """Default selected_model_view is the first in the list"""
        if len(self.model_views) > 0:
            return self.model_views[0]

    # Workflow Validation
    @on_trait_change('model_views.verify_workflow_event')
    def received_verify_request(self):
        """Pass on call for verify_workflow_event"""
        self.verify_workflow_event = True

    def _model_views_default(self):
        """A default constructor for this trait needs to be implemented"""
        raise NotImplementedError(
            "_model_views_default was not implemented in {}".format(
                self.__class__))

    def update_model_views(self):
        """Regenerates the model_views from the model and sets the
         default selected_model_view. This method can be combined with an
         on_trait_change decorator in a child class"""

        # Update the list of ModelView(s)
        self.model_views = self._model_views_default()

        # Update the selected_model_view
        self.selected_model_view = self._selected_model_view_default()
