from traits.api import Instance, Unicode, on_trait_change

from force_wfmanager.ui.setup.process.data_source_view import (
    DataSourceView
)
from force_wfmanager.ui.setup.process.execution_layer_view import (
    ExecutionLayerView
)
from force_wfmanager.ui.ui_utils import get_factory_name
from force_wfmanager.ui.setup.graph_display.box_utils import (
    InputOutputBox, SlotInfoBox, HLayoutBox
)
from force_wfmanager.ui.setup.graph_display.style_utils import (
    TextStyle, BoxStyle
)


class DataSourceBox(InputOutputBox):

    #: The data source view that we use.
    data_source_view = Instance(DataSourceView)

    #: The text to display.
    text = Unicode

    def _text_default(self):
        return get_factory_name(self.view.model.factory)

    @on_trait_change('data_source_view.input_slots_representation[]')
    def _update_input_slots(self):
        text_style = TextStyle(
            margin=2,
            alignment=('top', 'center')
        )
        self.inputs = []
        if self.data_source_view is not None:
            self.inputs += [
                SlotInfoBox(
                    model=input,
                    text_style=text_style,
                )
                for input in self.view.input_slots_representation
            ]

    @on_trait_change('data_source_view.output_slots_representation[]')
    def _update_output_slots(self):
        text_style = TextStyle(
            margin=2,
            alignment=('bottom', 'center')
        )
        self.outputs = []
        if self.data_source_view is not None:
            self.outputs += [
                SlotInfoBox(
                    model=output,
                    text_style=text_style)
                for output in self.view.output_slots_representation
            ]

    @on_trait_change('inputs.model.model.name')
    def _validate_inputs(self):
        valid_box_style = BoxStyle(
            color='azure'
        )
        invalid_box_style = BoxStyle(
            color='salmon'
        )
        for input in self.inputs:
            if input.model.model.name:
                input.box_style = valid_box_style
            else:
                input.box_style = invalid_box_style

    @on_trait_change('outputs.model.model.name')
    def _validate_outputs(self):
        valid_box_style = BoxStyle(
            color='azure'
        )
        inactive_box_style = BoxStyle(
            color='gainsboro'
        )
        for output in self.outputs:
            if output.model.model.name:
                output.box_style = valid_box_style
            else:
                output.box_style = inactive_box_style


class ExecutionLayerBox(HLayoutBox):

    #: The slot info model that we use.
    view = Instance(ExecutionLayerView)

    @on_trait_change('view.data_source_views[]')
    def _update_data_sources(self):
        iobox_style = BoxStyle(
            color='powderblue',
            rounded_corners={
                'top left', 'top right',
                'bottom left', 'bottom right'
            }
        )
        iotext_style = TextStyle(
            font="Swiss 18",
            line_height=24,
            margin=4,
            alignment=('center', 'center')
        )
        self.remove(*self.components)
        if self.view is not None:
            self.add(*[
                DataSourceBox(
                    model=data_source,
                    text_style=iotext_style,
                    box_style=iobox_style,
                )
                for data_source in self.view.data_source_views
            ])