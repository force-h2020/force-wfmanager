from traits.api import (
    HasTraits, List, Instance, Unicode, on_trait_change, Bool, Event
)

from force_bdss.api import Workflow

from force_wfmanager.ui.setup.mco.mco_view import MCOView
from force_wfmanager.ui.setup.process.process_view import (
    ProcessView
)
from force_wfmanager.ui.setup.communicator\
    .communicator_view import CommunicatorView
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)

# VerifierError severity constants
_ERROR = "error"
_WARNING = "warning"
_INFO = "information"


class WorkflowView(HasTraits):
    """A view containing information on certain aspects of the workflow
    state. This includes: Current errors, Available variables, Plugins loaded
    and the current workflow filename."""

    # -----------------------------
    # Required/Dependent Attributes
    # -----------------------------

    #: The Workflow model
    model = Instance(Workflow, allow_none=False)

    # -------------------
    # Required Attributes
    # -------------------

    #: The Variable Names Registry
    variable_names_registry = Instance(VariableNamesRegistry)

    # ------------------
    # Regular Attributes
    # ------------------

    #: Process to be displayed in the TreeEditor.
    #: NOTE: (Has to be a list to be selectable in TreeEditor)
    process_view = List(Instance(ProcessView))

    #: MCO to be displayed in the side pane
    #: NOTE: (Has to be a list to be selectable in TreeEditor)
    mco_view = List(Instance(MCOView))

    #: Notification listeners to be displayed in the side pane
    #: NOTE: (Has to be a list to be selectable in TreeEditor)
    communicator_view = List(Instance(CommunicatorView))

    #: Defines if the Workflow is valid or not. Set by the
    #: function map_verify_workflow
    valid = Bool(True)

    #: Event to request a verification check on the workflow
    verify_workflow_event = Event()

    #: An error message for the entire workflow
    error_message = Unicode()

    #: A label for the Workflow
    label = Unicode("Workflow")

    # Defaults
    def _model_default(self):
        return Workflow()

    def _variable_names_registry_default(self):
        return VariableNamesRegistry(workflow=self.model)

    def _process_view_default(self):
        return [ProcessView(
            model=self.model,
            variable_names_registry=self.variable_names_registry)]

    def _mco_view_default(self):
        if self.model.mco is not None:
            return [MCOView(
                model=self.model.mco,
                variable_names_registry=self.variable_names_registry)]
        else:
            return []

    def _communicator_view_default(self):
        return [CommunicatorView(
            model=self.model,
            variable_names_registry=self.variable_names_registry)]

    #: Listeners
    @on_trait_change('model')
    def update_process_view(self):
        self.process_view = self._process_view_default()

    @on_trait_change('model:mco')
    def update_mco_view(self):
        self.mco_view = self._mco_view_default()

    @on_trait_change('model')
    def update_communication_view(self):
        self.communicator_view = self._communicator_view_default()

    @on_trait_change('mco_view.verify_workflow_event,'
                     'process_view.verify_workflow_event,'
                     'communicator_view.verify_workflow_event')
    def received_verify_request(self):
        self.verify_workflow_event = True

    #: Public methods
    def set_mco(self, mco_model):
        """Set the MCO"""
        self.model.mco = mco_model

    def remove_execution_layer(self, layer):
        """Removes the execution layer from the model."""
        self.process_view[0].remove_execution_layer(layer)

    def remove_data_source(self, data_source):
        """Removes the execution layer from the model."""
        self.process_view[0].remove_data_source(data_source)

    def remove_notification_listener(self, notification_listener):
        """Removes the execution layer from the model."""
        self.communicator_view[0].remove_notification_listener(
            notification_listener
        )
