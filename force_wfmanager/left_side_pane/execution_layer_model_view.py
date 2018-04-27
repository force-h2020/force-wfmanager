from traits.api import Instance, String, Bool
from traitsui.api import ModelView

from force_bdss.core.execution_layer import ExecutionLayer


class ExecutionLayerModelView(ModelView):
    #: The model object this MV wraps
    model = Instance(ExecutionLayer)

    #: The label to display in the list
    label = String()

    #: True if the wrapped object is valid.
    valid = Bool(True)

    def add_data_source(self, data_source):
        """Adds the passed data source model to the model data sources."""
        self.model.data_sources.append(data_source)
