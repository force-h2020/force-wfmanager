from traits.api import Bool, Event, Instance, List, Unicode, on_trait_change
from traitsui.api import ModelView

from force_bdss.api import Workflow
from force_wfmanager.ui.setup.execution_layers.execution_layer_model_view\
    import ExecutionLayerModelView
from force_wfmanager.ui.setup.mco.mco_model_view import MCOModelView
from force_wfmanager.ui.setup.notification_listeners.\
    notification_listener_model_view import NotificationListenerModelView
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)
from force_wfmanager.ui.setup.mco.mco_info import MCOInfo


class WorkflowModelView(ModelView):

    # -------------------
    # Required Attributes
    # -------------------

    #: The Workflow model
    model = Instance(Workflow, allow_none=False)

    #: The Variable Names Registry
    variable_names_registry = Instance(VariableNamesRegistry)

    # ------------------
    # Regular Attributes
    # ------------------

    #: List of MCO to be displayed in the TreeEditor
    mco_mv = List(Instance(MCOInfo))

    #: List of DataSources to be displayed in the TreeEditor.
    #: Must be a list otherwise the tree editor will not consider it
    #: as a child.
    execution_layers_mv = List(Instance(ExecutionLayerModelView))

    #: The notification listeners ModelView.
    notification_listeners_mv = List(Instance(NotificationListenerModelView))

    #: Defines if the Workflow is valid or not. Set by the
    #: function verify_tree in workflow_tree.py
    valid = Bool(True)

    #: An error message for issues in this modelview. Set by the
    #: function verify_tree in workflow_tree.py
    error_message = Unicode()

    #: A label for the Workflow
    label = Unicode("Workflow")

    # ------------------
    # Derived Attributes
    # ------------------

    #: Event to request a verification check on the workflow
    #: Listens to:
    #: :func:`MCOModelView.verify_workflow_event
    #: <force_wfmanager.views.execution_layers.mco_model_view\
    #: .MCOModelView.verify_workflow_event>`,
    #: :func:`ExecutionLayerModelView.verify_workflow_event
    #: <force_wfmanager.views.execution_layers.execution_layer_model_view.\
    #: ExecutionLayerModelView.verify_workflow_event>`,
    #: :func:`NotificationListenerModelView.verify_workflow_event
    #: <force_wfmanager.views.execution_layers.\
    # notification_listener_model_view.\
    #: NotificationListenerModelView.verify_workflow_event>`
    verify_workflow_event = Event

    # Workflow Verification

    @on_trait_change('mco_mv.verify_workflow_event,'
                     'execution_layers_mv.verify_workflow_event,'
                     'notification_listeners_mv.verify_workflow_event')
    def received_verify_request(self):
        self.verify_workflow_event = True

    # Add/Set New Models

    def set_mco(self, mco_model):
        """Set the MCO"""
        self.model.mco = mco_model

    def add_execution_layer(self, execution_layer):
        """Adds a new empty execution layer"""
        self.model.execution_layers.append(execution_layer)

    def add_notification_listener(self, notification_listener):
        """Adds a new notification listener"""
        self.model.notification_listeners.append(notification_listener)

    # Remove Models

    def remove_execution_layer(self, layer):
        """Removes the execution layer from the model."""
        self.model.execution_layers.remove(layer)

    def remove_notification_listener(self, notification_listener):
        """Removes the notification listener from the model."""
        self.model.notification_listeners.remove(notification_listener)

    def remove_data_source(self, data_source):
        """Removes the data source from the model"""
        for execution_layer_mv in self.execution_layers_mv:
            if data_source in execution_layer_mv.model.data_sources:
                execution_layer_mv.remove_data_source(data_source)

    # Update the model views in response to changes in the model structure.

    @on_trait_change('model.mco')
    def update_mco_mv(self):
        """Updates the MCO model view with the model.mco changes"""
        if self.model.mco is not None:
            self.mco_mv = [MCOInfo(
                variable_names_registry=self.variable_names_registry,
                model=self.model.mco)]
        else:
            self.mco_mv = []

    @on_trait_change('model.execution_layers[]', post_init=True)
    def update_execution_layers_mv(self):
        """Update the ExecutionLayer ModelViews when the model changes."""
        self.execution_layers_mv = [
            ExecutionLayerModelView(
                model=execution_layer,
                layer_index=idx,
                variable_names_registry=self.variable_names_registry,
                label="Layer {}".format(idx)
            )
            for idx, execution_layer in enumerate(self.model.execution_layers)
        ]

    @on_trait_change("model.notification_listeners[]")
    def update_notification_listeners_mv(self):
        """Updates the modelviews for the notification listeners, but ignoring
        any which are non UI visible"""
        self.notification_listeners_mv = [
            NotificationListenerModelView(
                model=notification_listener,
            )
            for notification_listener in self.model.notification_listeners
            if notification_listener.factory.ui_visible is True
        ]

    # Defaults

    def _model_default(self):
        return Workflow()

    def _variable_names_registry_default(self):
        return VariableNamesRegistry(workflow=self.model)
