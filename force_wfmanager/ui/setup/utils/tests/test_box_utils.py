from unittest import TestCase

from force_wfmanager.ui.setup.utils.box_utils import (
    Box, TextBox, HLayoutBox, InputOutputBox
)
from force_wfmanager.ui.setup.utils.style_utils import (
    BoxStyle, TextStyle
)


class TestBox(TestCase):

    def setUp(self):

        self.box_style = BoxStyle()
        self.box = Box(
            box_style=self.box_style
        )

    def test___init__(self):

        self.assertEqual('azure', self.box.bgcolor)
        self.assertEqual('azure', self.box.border_color)


class TestTextBox(TestCase):

    def setUp(self):

        self.text_style = TextStyle()
        self.text_box = TextBox(
            text='some text',
            text_style=self.text_style
        )

    def test___init__(self):

        self.assertEqual('some text', self.text_box.text)

    def test_get_preferred_size(self):

        size = self.text_box.get_preferred_size()
        self.assertListEqual([62, 16], size)

        self.text_box.padding_left += 2
        self.text_box.padding_right += 2
        self.text_box.padding_top += 2
        self.text_box.padding_bottom += 2
        size = self.text_box.get_preferred_size()
        self.assertListEqual([66, 20], size)


class TestHLayoutBox(TestCase):

    def setUp(self):

        self.h_layout_box = HLayoutBox(
            text='some text'
        )

    def test___init__(self):

        self.assertEqual('some text', self.h_layout_box.text)
        self.assertEqual(10, self.h_layout_box.spacing)

    def test_get_preferred_size(self):
        size = self.h_layout_box.get_preferred_size()
        self.assertEqual((62, 36), size)

        self.h_layout_box.spacing += 2
        self.h_layout_box.padding_left += 2
        self.h_layout_box.padding_right += 2
        self.h_layout_box.padding_top += 2
        self.h_layout_box.padding_bottom += 2
        size = self.h_layout_box.get_preferred_size()
        self.assertEqual((70, 48), size)


class TestInputOutputBox(TestCase):

    def setUp(self):

        inputs = [TextBox(text=f'input box {i}') for i in range(2)]
        outputs = [TextBox(text=f'output box {i}') for i in range(2)]

        self.input_output_box = InputOutputBox(
            text='some text',
            inputs=inputs,
            outputs=outputs
        )

    def test___init__(self):

        self.assertEqual(4, len(self.input_output_box.components))

    def test_get_preferred_size(self):
        size = self.input_output_box.get_preferred_size()
        self.assertEqual((158, 48), size)

        self.input_output_box.padding_left += 2
        self.input_output_box.padding_right += 2
        self.input_output_box.padding_top += 2
        self.input_output_box.padding_bottom += 2
        size = self.input_output_box.get_preferred_size()
        self.assertEqual((162, 56), size)

        self.input_output_box.inputs[0].padding_left += 2
        self.input_output_box.outputs[0].padding_top += 2
        size = self.input_output_box.get_preferred_size()
        self.assertEqual((162, 58), size)

        self.input_output_box.inputs[0].padding_left += 20
        self.input_output_box.outputs[0].padding_top += 20
        size = self.input_output_box.get_preferred_size()
        self.assertEqual((182, 78), size)