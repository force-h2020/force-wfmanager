from traits.api import Instance, String, Bool
from traitsui.api import ModelView

from force_bdss.core.execution_layer import ExecutionLayer


class ExecutionLayerModelView(ModelView):
    model = Instance(ExecutionLayer)

    label = String()

    valid = Bool(True)
