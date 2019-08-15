from traits.api import (
    Instance, on_trait_change, Property, List
)

from force_wfmanager.ui.setup.graph_display.process_graph_objects import (
    ExecutionLayerBox
)
from force_wfmanager.ui.setup.mco.mco_view import MCOView
from force_wfmanager.ui.setup.graph_display.mco_graph_objects import (
    ParametersBox, KPIsBox
)
from force_wfmanager.ui.setup.graph_display.box_utils import (
    HLayoutBox
)
from force_wfmanager.ui.setup.graph_display.style_utils import (
    TextStyle
)
from force_wfmanager.ui.setup.graph_display.graph_utils import (
    LayeredGraph
)
from force_wfmanager.ui.setup.process.process_view import (
    ProcessView
)
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)


class WorkflowGraph(LayeredGraph):

    variable_names_registry = Instance(VariableNamesRegistry, allow_none=False)

    #: The workflow we are using.
    mco_view = Instance(MCOView)

    process_view = Property(Instance(ProcessView),
                            depends_on='variable_names_registry')

    parameters_layer = HLayoutBox(text="Parameters")

    kpis_layer = HLayoutBox(text="KPIs")

    execution_layers = List(Instance(ExecutionLayerBox))

    def _get_process_view(self):
        if self.variable_names_registry is not None:
            return self.variable_names_registry.process_view

    @on_trait_change(
        'process_view.execution_layer_views[],'
        'mco_view.[kpi_view,parameter_view]')
    def update_layers(self):

        self.parameters_layer.remove(*self.parameters_layer.components)
        self.kpis_layer.remove(*self.kpis_layer.components)
        self.execution_layers = []

        if self.process_view is not None:
            self.execution_layers = [
                ExecutionLayerBox(execution_layer_view=execution_layer_view)
                for execution_layer_view
                in self.process_view.execution_layer_views
            ]

        if self.mco_view is not None:
            self.parameters_layer.add(ParametersBox(
                parameter_view=self.mco_view.parameter_view,
                text_style=TextStyle(
                    alignment=('top', 'center')
                )
            ))

            self.kpis_layer.add(KPIsBox(
                kpi_view=self.mco_view.kpi_view,
                text_style=TextStyle(
                    alignment=('bottom', 'center')
                )
            ))

        self.remove(*self.components)
        self.add(self.kpis_layer)
        self.add(*reversed(self.execution_layers))
        self.add(self.parameters_layer)

    def get_connections_edit(self):
        connections = []
        sources = {}

        variables = self.variable_names_registry.available_variables

        for variable in variables:

            if variable.output_slot_row is not None:
                layer_index = variable.layer_index
                layer_box = self.execution_layers[layer_index]
                base_x, base_y = layer_box.position

                data_index = layer_box.execution_layer_view.data_source_views.index(
                    variable.origin
                )
                data_box = layer_box.components[data_index]
                base_x += data_box.x
                base_y += data_box.y

                slot_index = variable.output_slot_row.index
                output = data_box.outputs[slot_index]
                output_x = base_x + output.x
                output_y = base_y + output.y

                for input_row in variable.input_slot_rows:
                    layer_index = input_row[0]
                    layer_box = self.execution_layers[layer_index]
                    base_x, base_y = layer_box.position

                    data_index = [
                        index for index, data_box in
                        enumerate(layer_box.components)
                        if input_row[1] in data_box.data_source_view.input_slots_representation
                    ][0]
                    data_box = layer_box.components[data_index]
                    base_x += data_box.x
                    base_y += data_box.y

                    slot_index = input_row[1].index
                    input = data_box.inputs[slot_index]
                    input_x = base_x + input.x
                    input_y = base_y + input.y

                    connections.append(
                        [(output, (output_x, output_y)), (input, (input_x, input_y))]
                    )

        return connections