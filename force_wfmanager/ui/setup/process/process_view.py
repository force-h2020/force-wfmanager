from traits.api import (
    HasTraits, Instance, List, on_trait_change, Bool, Event, Unicode
)

from force_bdss.api import Workflow

from .execution_layer_view import ExecutionLayerView


class ProcessView(HasTraits):
    """A view object containing the process to optimise. This is a
    hierarchical construct consisting of execution layers containing
    data sources"""

    # -------------------
    # Required Attributes
    # -------------------

    #: The Process model
    model = Instance(Workflow)

    # ------------------
    # Regular Attributes
    # ------------------

    #: List of the data source's modelviews.
    #: Must be a list otherwise the tree editor will not consider it
    #: as a child.
    execution_layer_views = List(Instance(ExecutionLayerView))

    #: The label to display in the list
    label = Unicode('Process')

    # ---------------------
    #  Dependent Attributes
    # ---------------------

    #: Defines if the MCO is valid or not. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    valid = Bool(True)

    #: An error message for issues in this modelview. Updated by
    #: :func:`workflow_tree.WorkflowTree.verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    error_message = Unicode()

    #: An event which runs a verification check on the current workflow when
    #: triggered.
    #: Listens to: :func:`execution_layer_views.verify_workflow_event`
    verify_workflow_event = Event()

    # -------------------
    #     Listeners
    # -------------------

    @on_trait_change('model.execution_layers[]')
    def update_execution_layer_views(self):
        """Update the ExecutionLayer ModelViews when the model changes."""
        self.execution_layer_views = [
            ExecutionLayerView(
                model=execution_layer,
                layer_index=idx,
                label="Layer {}".format(idx)
            )
            for idx, execution_layer in enumerate(
                self.model.execution_layers)
        ]

    @on_trait_change('execution_layer_views.verify_workflow_event')
    def received_verify_request(self):
        """Fires :attr:`verify_workflow_event` when a data source contained
        in this execution layer fires its `verify_workflow_event`
        """
        self.verify_workflow_event = True

    # -------------------
    #   Public Methods
    # -------------------

    def add_execution_layer(self, execution_layer):
        """Adds a new empty execution layer"""
        self.model.execution_layers.append(execution_layer)

    def remove_execution_layer(self, layer):
        """Removes the execution layer from the model."""
        self.model.execution_layers.remove(layer)
        self.verify_workflow_event = True

    # NOTE: Currently needed by TreeEditor as a reference point
    def remove_data_source(self, data_source):
        """Removes the data source from the model"""
        for execution_layer_view in self.execution_layer_views:
            if data_source in execution_layer_view.model.data_sources:
                execution_layer_view.remove_data_source(data_source)
