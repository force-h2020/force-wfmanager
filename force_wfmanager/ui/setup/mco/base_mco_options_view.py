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

    #: List of option ModelViews to display in ListEditor notebook
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
        errors = []
        unique_check = True

        for model_view in self.model_views:
            if model_view.model.name in model_names:
                unique_check = False
            model_names.append(model_view.model.name)

        if not unique_check:
            errors.append(
                VerifierError(
                    subject=self,
                    global_error=(f'Two or more {self.name} have'
                                  ' a duplicate name'),
                )
            )

        return errors

    # ------------------
    #   Private Methods
    # ------------------

    def _create_model_view(self, model):
        """A method to return a model view for a given model trait
        needs to be implemented"""
        raise NotImplementedError(
            "_create_model_view was not implemented in {}".format(
                self.__class__))

    def _remove_button_action(self, remove_function):
        """A default set of actions to perform on firing of a button
        to remove selected_model_view"""

        index = self.model_views.index(self.selected_model_view)
        remove_function(self.selected_model_view.model)

        # Update user selection
        if len(self.model_views) > 0:
            if index == 0:
                self.selected_model_view = self.model_views[index]
            else:
                self.selected_model_view = self.model_views[index-1]

    # ------------------
    #   Public Methods
    # ------------------

    def update_model_views(self, mco_options=None):
        """Regenerates the model_views from the model and sets the
         default selected_model_view.

         This method can be combined with an
         on_trait_change decorator in a child class"""

        # Update the list of ModelView(s)
        new_model_views = []
        if mco_options is not None:
            # Check in case a model has been deleted from mco_options
            for model_view in self.model_views:
                if model_view.model in mco_options:
                    new_model_views.append(model_view)

            # Check in case a model has been added to mco_options
            models = [model_view.model for model_view in self.model_views]
            for model in mco_options:
                if model not in models:
                    model_view = self._create_model_view(model)
                    new_model_views.append(model_view)

        self.model_views = new_model_views

        # Update the selected_model_view
        self.selected_model_view = self._selected_model_view_default()
