from traits.api import (
    Instance, on_trait_change
)

from force_wfmanager.ui.setup.mco.kpi_specification_view import (
    KPISpecificationView
)
from force_wfmanager.ui.setup.mco.mco_parameter_view import (
    MCOParameterView
)
from force_wfmanager.ui.setup.graph_display.box_utils import (
    InputOutputBox, SlotInfoBox
)
from force_wfmanager.ui.setup.graph_display.style_utils import (
    BoxStyle, TextStyle
)


class ParametersBox(InputOutputBox):

    #: The data source that we use.
    parameter_view = Instance(MCOParameterView)

    #: The text to display.
    text = "Parameters"

    @on_trait_change('outputs.model.name')
    def _validate_outputs(self):
        valid_box_style = BoxStyle(
            color='azure'
        )
        inactive_box_style = BoxStyle(
            color='gainsboro'
        )
        for output in self.outputs:
            if output.model.name:
                output.box_style = valid_box_style
            else:
                output.box_style = inactive_box_style

    @on_trait_change('parameter_view.model_views[]')
    def _update_output_slots(self):
        text_style = TextStyle(
            margin=2,
            alignment=('bottom', 'center')
        )
        self.outputs = []
        if self.parameter_view is not None:
            self.outputs += [
                SlotInfoBox(model=model_view.model, text_style=text_style)
                for model_view in self.parameter_view.model_views
            ]


class KPIsBox(InputOutputBox):

    #: The data source that we use.
    kpi_view = Instance(KPISpecificationView)

    #: The text to display.
    text = "KPIs"

    @on_trait_change('inputs.model.name')
    def _validate_inputs(self):
        valid_box_style = BoxStyle(
            color='azure'
        )
        invalid_box_style = BoxStyle(
            color='salmon'
        )
        for input in self.inputs:
            if input.model.name:
                input.box_style = valid_box_style
            else:
                input.box_style = invalid_box_style

    @on_trait_change('kpi_view.model_views[]')
    def _update_input_slots(self):
        text_style = TextStyle(
            margin=2,
            alignment=('top', 'center')
        )
        self.inputs = []
        if self.kpi_view is not None:
            self.inputs += [
                SlotInfoBox(model=model_view.model, text_style=text_style)
                for model_view in self.kpi_view.model_views
            ]
