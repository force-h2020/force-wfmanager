from traits.api import Bool, Event, Instance, List, Unicode, on_trait_change
from traitsui.api import ModelView

from force_bdss.api import Workflow

from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)
from force_wfmanager.ui.setup.mco.mco_model_view import MCOModelView
from force_wfmanager.ui.setup.process.process_tree import ProcessTree
from force_wfmanager.ui.setup.notification_listeners.\
    notification_listeners_info import NotificationListenerInfo


class WorkflowModelView(ModelView):

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

    #: List of MCO to be displayed in the TreeEditor
    mco_model_view = List(Instance(MCOModelView))

    #: List of DataSources to be displayed in the TreeEditor.
    #: Must be a list otherwise the tree editor will not consider it
    #: as a child.
    process_tree = List(Instance(ProcessTree))

    communication_model_view = List(Instance(NotificationListenerInfo))

    #: Defines if the Workflow is valid or not. Set by the
    #: function verify_tree in process_tree.py
    valid = Bool(True)

    #: An error message for issues in this modelview. Set by the
    #: function verify_tree in process_tree.py
    error_message = Unicode()

    #: A label for the Workflow
    label = Unicode("Workflow")

    # ------------------
    # Derived Attributes
    # ------------------

    #: Event to request a verification check on the workflow
    #: Listens to:
    #: :func:`MCOModelView.verify_workflow_event
    #: <force_wfmanager.views.process.mco_model_view\
    #: .MCOModelView.verify_workflow_event>`,
    #: :func:`ExecutionLayerModelView.verify_workflow_event
    #: <force_wfmanager.views.process.execution_layer_model_view.\
    #: ExecutionLayerModelView.verify_workflow_event>`,
    #: :func:`NotificationListenerModelView.verify_workflow_event
    #: <force_wfmanager.views.process.\
    # notification_listener_model_view.\
    #: NotificationListenerModelView.verify_workflow_event>`
    verify_workflow_event = Event

    #: The factory currently selected in the SetupPane
    selected_factory = Unicode()

    #: Filename for the current workflow (if any)
    workflow_filename = Unicode()


    def set_mco(self, mco_model):
        """Set the MCO"""
        self.model.mco = mco_model

    def add_notification_listener(self, notification_listener):
        """Adds a new notification listener"""
        self.model.notification_listeners.append(notification_listener)

    def remove_notification_listener(self, notification_listener):
        """Removes the notification listener from the model."""
        self.model.notification_listeners.remove(notification_listener)



    # Workflow Verification

    @on_trait_change('mco_info.verify_workflow_event,'
                     'process_info.verify_workflow_event,'
                     'notification_listener_info.verify_workflow_event')
    def received_verify_request(self):
        self.verify_workflow_event = True

    # Add/Set New Models

    # Update the model views in response to changes in the model structure.

    # Defaults

    def _model_default(self):
        return Workflow()

    def _variable_names_registry_default(self):
        return VariableNamesRegistry(workflow=self.model)


    def _variable_names_registry_default(self):
        return VariableNamesRegistry(workflow=self.workflow_model)

    def _workflow_model_view_default(self):
        return WorkflowModelView(
            model=self.workflow_model,
            variable_names_registry=self.variable_names_registry
        )