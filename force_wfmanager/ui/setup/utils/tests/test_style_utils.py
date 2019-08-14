from unittest import TestCase

from enable.api import Component
from enable.compiled_path import CompiledPath
from traits.api import Set

from force_wfmanager.ui.setup.utils.style_utils import (
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

        self.text_style = TextStyle()
