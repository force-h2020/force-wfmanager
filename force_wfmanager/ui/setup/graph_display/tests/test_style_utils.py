from unittest import TestCase

from enable.api import Component
from enable.compiled_path import CompiledPath
from traits.api import Set

from force_wfmanager.ui.setup.graph_display.style_utils import (
    BaseStyle, BoxStyle, TextStyle
)


class TestBaseStyle(TestCase):

    def test___init__(self):
        base_style = BaseStyle()

        self.assertEqual(
            base_style.color,
            base_style.stroke_color
        )


class TestBoxStyle(TestCase):

    def setUp(self):

        self.box_style = BoxStyle(
            border_width=2,
            corner_radius=5
        )

    def test___init__(self):

        self.assertEqual(2, self.box_style.border_width)
        self.assertEqual(5, self.box_style.corner_radius)
        self.assertIsInstance(
            self.box_style.rounded_corners.trait, Set)
        self.assertIsNone(
            self.box_style.rounded_corners.trait.trait)

    def test_path(self):
        self.box_style.rounded_corners = {
            'top left', 'top right', 'bottom left', 'bottom right'
        }

        component = Component()

        path = self.box_style.path(
            component.outer_position + component.outer_bounds
        )

        self.assertIsInstance(path, CompiledPath)


class TestTextStyle(TestCase):

    def setUp(self):

        self.text_style = TextStyle(
            alignment=('top', 'left')
        )

    def test___init__(self):

        self.assertEqual('black', self.text_style.color)
        self.assertListEqual([0, 0, 0, 0], self.text_style.margin)
        self.assertEqual(0, self.text_style.hmargin)
        self.assertEqual(0, self.text_style.vmargin)
        self.assertEqual(16, self.text_style.line_height)

    def test_get_preferred_size(self):

        size = self.text_style.get_preferred_size('some text')
        self.assertEqual((62.0, 16), size)

        self.text_style.line_height = 12
        size = self.text_style.get_preferred_size('some text')
        self.assertEqual((62.0, 12), size)

        self.text_style.margin_bottom = 2
        size = self.text_style.get_preferred_size('some text')
        self.assertEqual((62.0, 14), size)

        self.text_style.margin_top = 2
        size = self.text_style.get_preferred_size('some text')
        self.assertEqual((62.0, 16), size)

        self.text_style.margin_left = 2
        size = self.text_style.get_preferred_size('some text')
        self.assertEqual((64.0, 16), size)

        self.text_style.margin_right = 2
        size = self.text_style.get_preferred_size('some text')
        self.assertEqual((66.0, 16), size)

    def test_align_text(self):

        box = Component()
        offsets = self.text_style.align_text(None, box, 'some text')
        self.assertEqual((0, -12), offsets)

        self.text_style.margin_left = 2
        self.text_style.margin_top = 2
        offsets = self.text_style.align_text(None, box, 'some text')
        self.assertEqual((2, -14), offsets)

        self.text_style.alignment = ('center', 'left')
        offsets = self.text_style.align_text(None, box, 'some text')
        self.assertEqual((2, -5.5), offsets)

        self.text_style.margin_top = 0
        offsets = self.text_style.align_text(None, box, 'some text')
        self.assertEqual((2, -4.5), offsets)

        self.text_style.alignment = ('bottom', 'left')
        offsets = self.text_style.align_text(None, box, 'some text')
        self.assertEqual((2, 4), offsets)

        self.text_style.margin_bottom = 2
        self.text_style.line_height += 2
        offsets = self.text_style.align_text(None, box, 'some text')
        self.assertEqual((2, 8), offsets)

        self.text_style.alignment = ('bottom', 'center')
        offsets = self.text_style.align_text(None, box, 'some text')
        self.assertEqual((-30, 8), offsets)

        self.text_style.margin_left += 2
        offsets = self.text_style.align_text(None, box, 'some text')
        self.assertEqual((-29, 8), offsets)

        self.text_style.alignment = ('bottom', 'right')
        offsets = self.text_style.align_text(None, box, 'some text')
        self.assertEqual((-62, 8), offsets)

        self.text_style.margin_right += 2
        offsets = self.text_style.align_text(None, box, 'some text')
        self.assertEqual((-64, 8), offsets)

