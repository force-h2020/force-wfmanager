from traits.api import Instance, String, Bool, on_trait_change, List, Int
from traitsui.api import ModelView

from force_bdss.api import ExecutionLayer
from force_wfmanager.left_side_pane.data_source_model_view import \
    DataSourceModelView
from force_wfmanager.left_side_pane.variable_names_registry import \
    VariableNamesRegistry


class ExecutionLayerModelView(ModelView):
    #: The model object this MV wraps
    model = Instance(ExecutionLayer)

    layer_index = Int()

    #: Registry of the available variables
    variable_names_registry = Instance(VariableNamesRegistry)

    #: List of the data sources modelviews.
    data_sources_mv = List(Instance(DataSourceModelView))

    #: The label to display in the list
    label = String()

    #: True if the wrapped object is valid.
    valid = Bool(True)

    def add_data_source(self, data_source):
        """Adds the passed data source model to the model data sources."""
        self.model.data_sources.append(data_source)

    def remove_data_source(self, data_source):
        self.model.data_sources.remove(data_source)

    @on_trait_change("model.data_sources[]")
    def update_data_sources_mv(self):
        self.data_sources_mv = [
            DataSourceModelView(
                layer_index=self.layer_index,
                model=data_source,
                variable_names_registry=self.variable_names_registry
            ) for data_source in self.model.data_sources]
