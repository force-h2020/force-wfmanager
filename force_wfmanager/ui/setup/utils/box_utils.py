from enable.api import Component, Container
from traits.api import (
    on_trait_change, Instance, Int, Unicode, List
)

from .style_utils import BoxStyle, TextStyle


class Box(Component):

    #: The style to use when drawing the box.
    box_style = Instance(BoxStyle, ())

    @on_trait_change('box_style')
    def update_colors(self):
        """Delegate both the background color and border color to
        the box_style trait"""
        self.bgcolor = self.box_style.color
        self.border_color = self.box_style.stroke_color

    def _draw_background(self, gc, view_bounds=None, mode="default"):
        self.box_style.draw_background(self, gc, view_bounds=None,
                                       mode="default")


class TextBox(Box):
    """ A component containing a text label.

    For simplicity, the text is assumed to be a single line.
    """

    #: The text to display.
    text = Unicode

    #: The style to use when drawing the text.
    text_style = Instance(TextStyle, ())

    def get_preferred_size(self):
        width, height = self.text_style.get_preferred_size(self.text)
        width += self.hpadding
        height += self.vpadding
        return [width, height]

    def _draw_mainlayer(self, gc, view_bounds=None, mode="default"):
        self.text_style.draw_mainlayer(self, gc, view_bounds=None,
                                       mode="default")

    def _text_changed(self):
        self._layout_needed = True
        self.invalidate_and_redraw()


class HLayoutBox(TextBox, Container):

    #: The amount of space between components.
    spacing = Int(10)

    def get_preferred_size(self):
        width, height = super(HLayoutBox, self).get_preferred_size()

        max_component_height = 0
        component_width = self.spacing * (len(self.components) + 1)

        for component in self.components:
            item_width, item_height = component.get_preferred_size()
            max_component_height = max(max_component_height, item_height)
            component_width += item_width

        width = max(width, component_width)
        height += max_component_height + self.spacing * 2
        width += self.hpadding
        height += self.vpadding
        return width, height

    def _do_layout(self):
        if self.components:
            width, _ = self.get_preferred_size()
            spacing = self.spacing + (self.width - width) / (len(self.components) + 1)
            x = spacing
            y = self.text_style.get_preferred_size(self.text)[1] + self.spacing
            height = max(
                component.get_preferred_size()[1] for component in self.components
            )
            for component in self.components:
                component.width = component.get_preferred_size()[0] - component.hpadding
                component.height = height - component.vpadding
                component.outer_x = x
                if self.text_style.alignment[0] == 'top':
                    component.outer_y2 = self.height - y
                else:
                    component.outer_y = y

                x += component.outer_width + spacing

    def _draw_container_mainlayer(self, gc, view_bounds=None, mode="normal"):
        self._draw_mainlayer(gc, view_bounds=None, mode="normal")


class InputOutputBox(TextBox, Container):

    #: The inputs.
    inputs = List(Instance(TextBox))

    #: The inputs.
    outputs = List(Instance(TextBox))

    @on_trait_change('inputs[],outputs[]')
    def _update_inputs_outputs(self):
        self.remove(*self.components)
        self.add(*self.inputs)
        self.add(*self.outputs)

    def get_preferred_size(self):
        width, height = super(InputOutputBox, self).get_preferred_size()

        if self.inputs:
            max_input_width = max(
                input.get_preferred_size()[0] for input in self.inputs
            )
            max_input_height = max(
                input.get_preferred_size()[1] for input in self.inputs
            )
        else:
            max_input_width = 0
            max_input_height = 0
        input_width = max_input_width * len(self.inputs)

        if self.outputs:
            max_output_width = max(
                output.get_preferred_size()[0] for output in self.outputs
            )
            max_output_height = max(
                output.get_preferred_size()[1] for output in self.outputs
            )
        else:
            max_output_width = 0
            max_output_height = 0
        output_width = max_output_width * len(self.outputs)

        width = max(width, input_width, output_width)
        height = height + max_input_height + max_output_height
        width += self.hpadding
        height += self.vpadding
        return width, height

    def _do_layout(self):
        if self.inputs:
            width = self.width/len(self.inputs)
            height = max(
                input.get_preferred_size()[1] for input in self.inputs
            )
            for i, input in enumerate(self.inputs):
                input.bounds = [width, height]
                input.x = i * width
                input.y2 = self.height - self.border_width

        if self.outputs:
            width = self.width/len(self.outputs)
            height = max(
                output.get_preferred_size()[1] for output in self.outputs
            )
            for i, output in enumerate(self.outputs):
                _, height = output.get_preferred_size()
                output.bounds = [width, height]
                output.x = i * width
                output.y = 0

    def _draw_container_mainlayer(self, gc, view_bounds=None, mode="normal"):
        self._draw_mainlayer(gc, view_bounds=None, mode="normal")
