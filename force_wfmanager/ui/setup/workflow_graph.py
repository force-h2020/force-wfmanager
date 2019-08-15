from traits.api import (
    Instance, on_trait_change, Property, List
)

from force_wfmanager.ui.setup.graph_display.box_utils import (
    HLayoutBox
)
from force_wfmanager.ui.setup.graph_display.graph_utils import (
    LayeredGraph
)
from force_wfmanager.ui.setup.graph_display.mco_graph_objects import (
    ParametersBox, KPIsBox
)
from force_wfmanager.ui.setup.graph_display.process_graph_objects import (
    ExecutionLayerBox
)
from force_wfmanager.ui.setup.graph_display.style_utils import (
    TextStyle, BoxStyle
)
from force_wfmanager.ui.setup.mco.mco_view import MCOView
from force_wfmanager.ui.setup.process.process_view import (
    ProcessView
)
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)


class WorkflowGraph(LayeredGraph):
    """This class generates a graph view of the current state of the Workflow,
    which is displayed in the UI. This is built from the enable objects defined
    within force_wfmanager.ui.setup.graph_display"""

    # -------------------
    # Required Attributes
    # -------------------

    #: The Variable Names Registry containing all Variable objects
    #: parsed from the DataSource output and input slots, this provides
    #: information on how each variable is passed within the workflow
    variable_names_registry = Instance(VariableNamesRegistry, allow_none=False)

    #: MCO view containing information about the MCO
    mco_view = Instance(MCOView)

    # ------------------
    # Regular Attributes
    # ------------------

    #: Graph layer referring to the MCO Parameters
    parameters_layer = Instance(HLayoutBox)

    #: Graph layer referring to the MCO KPIs
    kpis_layer = Instance(HLayoutBox)

    #: Graph layers referring to each ExecutionLayerDataSource
    execution_layers = List(Instance(ExecutionLayerBox))

    # -------------------
    #      Properties
    # -------------------

    #: Quick reference to the process view, which contains information on
    #: all the execution layers
    process_view = Property(Instance(ProcessView),
                            depends_on='variable_names_registry')

    def _mco_layer_box(self, text):
        return HLayoutBox(
            text=text,
            text_style=TextStyle(
                font="Swiss 18",
                line_height=18,
                margin=2,
                alignment=('top', 'left')
            )
        )

    def _kpis_layer_default(self):
        return self._mco_layer_box('KPIs')

    def _parameters_layer_default(self):
        return self._mco_layer_box('Parameters')

    def _get_process_view(self):
        if self.variable_names_registry is not None:
            return self.variable_names_registry.process_view

    @on_trait_change(
        'process_view.execution_layer_views[],'
        'mco_view,parameter_view')
    def update_layers(self):
        """Update all components of the graph display"""

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
            box_style = BoxStyle(
                color='powderblue',
                rounded_corners={'top left', 'top right',
                                 'bottom left', 'bottom right'}
            )

            self.parameters_layer.add(ParametersBox(
                parameter_view=self.mco_view.parameter_view,
                box_style=box_style,
                text_style=TextStyle(
                    font="Swiss 18",
                    alignment=('top', 'center')
                )
            ))

            self.kpis_layer.add(KPIsBox(
                kpi_view=self.mco_view.kpi_view,
                box_style=box_style,
                text_style=TextStyle(
                    font="Swiss 18",
                    alignment=('bottom', 'center')
                )
            ))

        self.remove(*self.components)

        self.add(self.parameters_layer)
        self.add(*self.execution_layers)
        self.add(self.kpis_layer)

    def get_connections(self):
        """Overloads the get_connections_edit method to identify connections
        between slots using Variable objects listed in variable_names_registry,
        rather than simply the names of each slot."""

        connections = []

        parameter_refs = []
        kpi_refs = []

        if self.mco_view is not None:
            # Collate MCOParameter name / type combinations
            parameter_refs += [
                (parameter.model.name, parameter.model.type)
                for parameter in self.mco_view.parameter_view.model_views
            ]
            kpi_refs += [
                (kpi.model.name,)
                for kpi in self.mco_view.kpi_view.model_views
            ]

        variables = self.variable_names_registry.available_variables

        for variable in variables:

            kpi_key = (variable.name,)
            parameter_key = (variable.name, variable.type)

            if variable.output_slot_row is not None:
                layer_index = variable.layer_index
                layer_box = self.execution_layers[layer_index]
                output_x, output_y = layer_box.position

                views = layer_box.execution_layer_view.data_source_views
                data_index = views.index(variable.origin)
                data_box = layer_box.components[data_index]
                output_x += data_box.x
                output_y += data_box.y

                slot_index = variable.output_slot_row.index
                output = data_box.outputs[slot_index]

                for input_row in variable.input_slot_rows:
                    layer_index = input_row[0]
                    layer_box = self.execution_layers[layer_index]
                    input_x, input_y = layer_box.position

                    data_index = [
                        index for index, data_box in
                        enumerate(layer_box.components)
                        if input_row[1] in (
                            data_box.data_source_view.
                            input_slots_representation
                        )][0]
                    data_box = layer_box.components[data_index]
                    input_x += data_box.x
                    input_y += data_box.y

                    slot_index = input_row[1].index
                    input = data_box.inputs[slot_index]

                    connections.append(
                        [(output, (output_x, output_y)),
                         (input, (input_x, input_y))]
                    )

                if kpi_key in kpi_refs:
                    input_x, input_y = self.kpis_layer.position
                    layer_box = self.kpis_layer.components[0]
                    input_x += layer_box.x
                    input_y += layer_box.y

                    slot_index = kpi_refs.index(kpi_key)
                    input = layer_box.inputs[slot_index]

                    connections.append(
                        [(output, (output_x, output_y)),
                         (input, (input_x, input_y))]
                    )

            elif parameter_key in parameter_refs:
                output_x, output_y = self.parameters_layer.position
                layer_box = self.parameters_layer.components[0]
                output_x += layer_box.x
                output_y += layer_box.y

                slot_index = parameter_refs.index(parameter_key)
                output = layer_box.outputs[slot_index]

                for input_row in variable.input_slot_rows:
                    layer_index = input_row[0]
                    layer_box = self.execution_layers[layer_index]
                    input_x, input_y = layer_box.position

                    data_index = [
                        index for index, data_box in
                        enumerate(layer_box.components)
                        if input_row[1] in (
                            data_box.data_source_view
                            .input_slots_representation
                        )][0]
                    data_box = layer_box.components[data_index]
                    input_x += data_box.x
                    input_y += data_box.y

                    slot_index = input_row[1].index
                    input = data_box.inputs[slot_index]

                    connections.append(
                        [(output, (output_x, output_y)),
                         (input, (input_x, input_y))]
                    )

        return connections
