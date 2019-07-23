from traits.api import (
    Bool, Event, Instance, List, Unicode,
    on_trait_change, HasTraits, Property
)

from force_bdss.api import BaseMCOModel
from force_bdss.core.verifier import VerifierError

from force_wfmanager.ui.setup.mco.base_mco_options_model_view import (
    BaseMCOOptionsModelView
)
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
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

    #: Defines the human readable name for the View
    name = Unicode('Options')

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

    # ------------------
    # Dependent Attributes
    # ------------------

    #: The human readable name of the KPI View
    label = Property(Instance(Unicode), depends_on='name')

    def __init__(self, model=None, *args, **kwargs):
        super(BaseMCOOptionsView, self).__init__(*args, **kwargs)
        if model is not None:
            self.model = model

    # ------------------
    #      Defaults
    # ------------------

    def _selected_model_view_default(self):
        """Default selected_model_view is the first in the list"""
        if len(self.model_views) > 0:
            return self.model_views[0]

    def _model_views_default(self):
        """A default constructor for this trait needs to be implemented"""
        raise NotImplementedError(
            "_model_views_default was not implemented in {}".format(
                self.__class__))

    # ------------------
    #     Listeners
    # ------------------

    def _get_label(self):
        if self.name is not None:
            return f'MCO {self.name}'

    # Workflow Validation
    @on_trait_change('model_views.verify_workflow_event')
    def received_verify_request(self):
        """Pass on call for verify_workflow_event"""
        self.verify_workflow_event = True

    @on_trait_change('model_views.model.name')
    def verify_model_names(self):
        """Reports a validation warning if duplicate KPI names exist
        """
        model_names = []
        for model_view in self.model_views:
            model_names.append(model_view.model.name)

        errors = []
        unique_check = True

        for name in model_names:
            if model_names.count(name) > 1:
                unique_check = False

        if not unique_check:
            errors.append(
                VerifierError(
                    subject=self,
                    global_error=f'Two or more {self.name} have a duplicate name',
                )
            )

        return errors

    # ------------------
    #   Public Methods
    # ------------------

    def update_model_views(self):
        """Regenerates the model_views from the model and sets the
         default selected_model_view. This method can be combined with an
         on_trait_change decorator in a child class"""

        # Update the list of ModelView(s)
        self.model_views = self._model_views_default()

        # Update the selected_model_view
        self.selected_model_view = self._selected_model_view_default()
