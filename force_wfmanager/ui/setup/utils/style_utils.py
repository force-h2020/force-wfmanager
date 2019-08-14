from enable.api import ColorTrait
from enable.compiled_path import CompiledPath
from enable.font_metrics_provider import font_metrics_provider
from kiva.trait_defs.api import KivaFont
from traits.api import (
    Any, Dict, Enum, HasTraits, Int,
    Property, Set, Tuple, cached_property, on_trait_change
)

Corner = Enum('top left', 'top right', 'bottom right', 'bottom left')


class BaseStyle(HasTraits):

    #: The color for the style.
    color = ColorTrait('azure')

    #: The stroke color for the style.
    stroke_color = ColorTrait('slategray')

    def _stroke_color_default(self):
        return self.color


class BoxStyle(BaseStyle):

    #: The width of the border.
    border_width = Int(1)

    #: Radius for rounded corners.
    corner_radius = Int(7)

    #: The corners which are rounded.
    rounded_corners = Set(Corner)

    def path(self, rect):
        """ Create a rounded path for the supplied rectangle """
        x, y, w, h = rect
        x2 = x + w
        y2 = y + h
        r = self.corner_radius

        path = CompiledPath()
        if "bottom left" in self.rounded_corners:
            path.move_to(x + r, y)
            path.arc_to(x, y, x, y + r, r)
        else:
            path.move_to(x, y)

        if "top left" in self.rounded_corners:
            path.line_to(x, y2 - r)
            path.arc_to(x, y2, x + r, y2, r)
        else:
            path.line_to(x, y2)

        if "top right" in self.rounded_corners:
            path.line_to(x2 - r, y2)
            path.arc_to(x2, y2, x2, y2 - r, r)
        else:
            path.line_to(x2, y2)

        if "bottom right" in self.rounded_corners:
            path.line_to(x2, y + r)
            path.arc_to(x2, y, x2 - r, y, r)
        else:
            path.line_to(x2, y)

        path.close_path()

        return path

    def draw_background(self, component, gc, view_bounds=None, mode="default"):
        with gc:
            gc.set_fill_color(self.color_)
            gc.set_stroke_color(self.stroke_color_)
            gc.add_path(self.path(
                component.outer_position + component.outer_bounds
            ))
            gc.draw_path()


class TextStyle(BaseStyle):

    #: The color for the style.
    color = 'black'

    #: The font to use.
    font = KivaFont("Swiss 12", invalidate_cache=True)

    #: The number of pixels between lines.
    line_height = Int(16)

    #: How text is aligned relative to its bounding box.
    alignment = Tuple(
        Enum('top', 'center', 'bottom'),
        Enum('left', 'center', 'right')
    )

    #: The amount of space to put on the left side of the text
    margin_left = Int(0)

    #: The amount of space to put on the right side of the text
    margin_right = Int(0)

    #: The amount of space to put on top of the text
    margin_top = Int(0)

    #: The amount of space to put below the text
    margin_bottom = Int(0)

    #: This property allows a way to set the margin in bulk.  It can either be
    #: set to a single Int (which sets margin on all sides) or a tuple/list of
    #: 4 Ints representing the left, right, top, bottom margin amounts.  When
    #: it is read, this property always returns the margin as a list of four
    #: elements even if they are all the same.
    margin = Property(depends_on='margin_+')

    #: Readonly property expressing the total amount of horizontal margin
    hmargin = Property(Int, depends_on='margin_+')

    #: Readonly property expressing the total amount of vertical margin
    vmargin = Property(Int, depends_on='margin_+')

    #: A cache of text layout values.
    _metrics = Any

    #: A cache of text layout values.
    _text_cache = Dict

    def get_preferred_size(self, text):
        if text not in self._text_cache:
            self._text_cache[text] = self._metrics.get_text_extent(text)

        _, _, width, _ = self._text_cache[text]
        return width + self.hmargin, self.line_height + self.vmargin

    def align_text(self, gc, box, text):
        if text not in self._text_cache:
            self._text_cache[text] = self._metrics.get_text_extent(text)

        leading, descent, text_width, text_height = self._text_cache[text]

        x_offset = leading
        if self.alignment[1] == 'left':
            x_offset += self.margin_left
        elif self.alignment[1] == 'center':
            x_offset += (box.width - self.hmargin - text_width) / 2
            x_offset += self.margin_left
        elif self.alignment[1] == 'right':
            x_offset += box.width - text_width
            x_offset -= self.margin_right

        y_offset = 0
        if self.alignment[0] == 'top':
            y_offset += box.height - self.font.size - self.margin_top
        elif self.alignment[0] == 'center':
            y_offset += (box.height - self.vmargin - text_height) / 2
            y_offset += self.margin_bottom
        elif self.alignment[0] == 'bottom':
            y_offset += self.margin_bottom + self.line_height - self.font.size
            #y_offset -= descent

        return x_offset, y_offset

    def draw_mainlayer(self, component, gc, view_bounds=None, mode="default"):
        with gc:
            gc.set_font(self.font)
            gc.set_fill_color(self.color_)
            gc.set_stroke_color(self.stroke_color_)

            x_offset, y_offset = self.align_text(gc, component, component.text)
            gc.set_text_position(component.x + x_offset, component.y + y_offset)
            gc.show_text(component.text)

            gc.draw_path()

    def _get_margin(self):
        return [
            self.margin_left,
            self.margin_right,
            self.margin_top,
            self.margin_bottom
        ]

    def _set_margin(self, val):
        old_margin = self.margin

        if type(val) == int:
            self.margin_left = self.margin_right = val
            self.margin_top = self.margin_bottom = val
            self.trait_property_changed("margin", old_margin, [val]*4)
        else:
            # assume margin is some sort of array type
            if len(val) != 4:
                raise RuntimeError("margin must be a 4-element sequence "
                                   "type or an int.  Instead, got" + str(val))
            self.margin_left = val[0]
            self.margin_right = val[1]
            self.margin_top = val[2]
            self.margin_bottom = val[3]
            self.trait_property_changed("margin", old_margin, val)

    @cached_property
    def _get_hmargin(self):
        return self.margin_right + self.margin_left

    @cached_property
    def _get_vmargin(self):
        return self.margin_bottom + self.margin_top

    @on_trait_change('+invalidate_cache')
    def _invalidate_cache(self):
        self._text_cache = {}

    def _font_changed(self, new):
        self._metrics.set_font(new)

    def __metrics_default(self):
        metrics = font_metrics_provider()
        metrics.set_font(self.font)
        return metrics