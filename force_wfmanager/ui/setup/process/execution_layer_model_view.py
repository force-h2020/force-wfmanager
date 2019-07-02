from traits.api import (Instance, Unicode, Bool, on_trait_change, List, Int,
                        Event, HasTraits)
from traitsui.api import ModelView

from force_bdss.api import ExecutionLayer

from .data_source_model_view import \
    DataSourceModelView
from force_wfmanager.utils.variable_names_registry import \
    VariableNamesRegistry


class ExecutionLayerModelView(HasTraits):

    # -------------------
    # Required Attributes
    # -------------------

    #: The model object this MV wraps
    model = Instance(ExecutionLayer)

    #: The index of this execution layer.
    layer_index = Int()

    #: Registry of the available variables
    variable_names_registry = Instance(VariableNamesRegistry)

    #: The label to display in the list
    label = Unicode()

    # ------------------
    # Regular Attributes
    # ------------------

    #: List of the data source's modelviews.
    data_source_model_views = List(Instance(DataSourceModelView))

    # --------------------
    # Dependent Attributes
    # --------------------

    #: True if the model attribute of this modelview is valid. Updated by
    #: :func:`workflow_tree.WorkflowTree.verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    valid = Bool(True)

    #: An error message for issues in this modelview. Updated by
    #: :func:`workflow_tree.WorkflowTree.verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    error_message = Unicode()

    #: Event to request a verification check on the workflow
    #: Listens to: :attr:`data_sources_mv.verify_workflow_event
    #: <force_wfmanager.ui.setup.execution_layer.data_source_model_view.\
    #: DataSourceModelView.verify_workflow_event>`
    verify_workflow_event = Event()

    # Synchronizing UI and model
    @on_trait_change("model.data_sources[]")
    def update_data_source_model_views(self):
        """Updates the data source modelviews on a change in the underlying
        data source model. """
        self.data_source_model_views = [
            DataSourceModelView(
                layer_index=self.layer_index,
                model=data_source,
                variable_names_registry=self.variable_names_registry
            ) for data_source in self.model.data_sources]


    # Workflow Verification
    @on_trait_change('data_source_model_views.verify_workflow_event')
    def received_verify_request(self):
        """Fires :attr:`verify_workflow_event` when a data source contained
        in this execution layer fires its `verify_workflow_event`
        """
        self.verify_workflow_event = True

    # Data Source Actions

    def add_data_source(self, data_source):
        """Adds the passed data source model to this execution layer model's
        data sources list.

        Parameters
        ----------
        data_source: BaseDataSource
            The data source being added to this execution layer.
        """
        self.model.data_sources.append(data_source)

    def remove_data_source(self, data_source):
        """Removes the passed data source model from this execution layer
         model's data sources list

        Parameters
        ----------
        data_source: BaseDataSource
            The data source being removed from this execution layer.
         """
        self.model.data_sources.remove(data_source)
