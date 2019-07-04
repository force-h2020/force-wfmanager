from traits.api import (
    HasTraits, Instance, List, on_trait_change, Bool, Event, Unicode
)
from traitsui.api import ModelView
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)
from .execution_layer_model_view import ExecutionLayerModelView
from force_bdss.api import Workflow


class ProcessModelView(HasTraits):
    # -------------------
    # Required Attributes
    # -------------------

    #: The Process model
    model = Instance(Workflow)

    #: The Variable Names Registry
    variable_names_registry = Instance(VariableNamesRegistry)

    #: The label to display in the list
    label = Unicode('Process')

    # ------------------
    # Regular Attributes
    # ------------------

    #: List of the data source's modelviews.
    #: Must be a list otherwise the tree editor will not consider it
    #: as a child.
    execution_layer_model_views = List(Instance(ExecutionLayerModelView))

    valid = Bool(True)

    #: An event which runs a verification check on the current workflow when
    #: triggered.
    #: Listens to: :func:`~workflow_mv.verify_workflow_event`
    verify_workflow_event = Event

    def __init__(self, model, *args, **kwargs):
        super(ProcessModelView, self).__init__(*args, **kwargs)
        self.model = model

    @on_trait_change('model.execution_layers[]')
    def update_execution_layers_mv(self):
        """Update the ExecutionLayer ModelViews when the model changes."""
        self.execution_layer_model_views = [
            ExecutionLayerModelView(
                model=execution_layer,
                layer_index=idx,
                variable_names_registry=self.variable_names_registry,
                label="Layer {}".format(idx)
            )
            for idx, execution_layer in enumerate(
                self.model.execution_layers)
        ]

    @on_trait_change('execution_layer_model_views.verify_workflow_event')
    def received_verify_request(self):
        """Fires :attr:`verify_workflow_event` when a data source contained
        in this execution layer fires its `verify_workflow_event`
        """
        self.verify_workflow_event = True

    def add_execution_layer(self, execution_layer):
        """Adds a new empty execution layer"""
        self.model.execution_layers.append(execution_layer)

    # Remove Models

    def remove_execution_layer(self, layer):
        """Removes the execution layer from the model."""
        self.model.execution_layers.remove(layer)

    def remove_data_source(self, data_source):
        """Removes the data source from the model"""
        for execution_layer_mv in self.execution_layer_model_views:
            if data_source in execution_layer_mv.model.data_sources:
                execution_layer_mv.remove_data_source(data_source)

