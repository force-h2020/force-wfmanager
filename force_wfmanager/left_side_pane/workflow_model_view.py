from traits.api import Instance, List, Bool, on_trait_change

from traitsui.api import ModelView

from force_bdss.core.workflow import Workflow
from force_wfmanager.left_side_pane.execution_layer_model_view import \
    ExecutionLayerModelView
from force_wfmanager.left_side_pane.mco_model_view import MCOModelView
from force_wfmanager.left_side_pane.notification_listener_model_view import \
    NotificationListenerModelView
from force_wfmanager.left_side_pane.variable_names_registry import \
    VariableNamesRegistry


class WorkflowModelView(ModelView):
    #: Workflow model
    model = Instance(Workflow, allow_none=False)

    #: List of MCO to be displayed in the TreeEditor
    mco_mv = List(Instance(MCOModelView))

    #: List of DataSources to be displayed in the TreeEditor.
    #: Must be a list otherwise the tree editor will not consider it
    #: as a child.
    execution_layers_mv = List(Instance(ExecutionLayerModelView))

    #: The notification listeners ModelView.
    notification_listeners_mv = List(Instance(NotificationListenerModelView))

    #: Variable Names Registry
    variable_names_registry = Instance(VariableNamesRegistry)

    #: Defines if the Workflow is valid or not
    valid = Bool(True)

    def set_mco(self, mco_model):
        self.model.mco = mco_model

    def add_execution_layer(self, execution_layer):
        """Adds a new empty execution layer"""
        self.model.execution_layers.append(execution_layer)

    def remove_execution_layer(self, layer):
        """Removes the execution layer from the model."""
        self.model.execution_layers.remove(layer)

    def add_notification_listener(self, notification_listener):
        """Adds a new empty execution layer"""
        self.model.notification_listeners.append(notification_listener)

    def remove_notification_listener(self, notification_listener):
        """Removes the execution layer from the model."""
        self.model.notification_listeners.remove(notification_listener)

    # Update the model views in response to changes in the model structure.

    @on_trait_change('model.mco')
    def update_mco_mv(self):
        """Updates the MCO model view with the model.mco changes"""
        if self.model.mco is not None:
            self.mco_mv = [MCOModelView(
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
        self.notification_listeners_mv = [
            NotificationListenerModelView(
                model=notification_listener,
            )
            for notification_listener in self.model.notification_listeners
        ]

    def _model_default(self):
        return Workflow()

    def _variable_names_registry_default(self):
        return VariableNamesRegistry(workflow=self.model)
