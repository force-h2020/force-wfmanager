from unittest import TestCase

from enable.api import Component

from force_wfmanager.ui.setup.utils.box_utils import (
    TextBox, InputOutputBox, HLayoutBox
)
from force_wfmanager.ui.setup.utils.graph_utils import (
    LayeredGraph
)


class TestLayeredGraph(TestCase):

    def setUp(self):

        inputs = [TextBox(text=f'input box {i}') for i in range(2)]
        outputs = [TextBox(text=f'output box {i}') for i in range(2)]

        self.input_output_box = InputOutputBox(
            text='some text',
            inputs=inputs,
            outputs=outputs
        )

        self.h_layout_box = HLayoutBox()
        self.h_layout_box.add(self.input_output_box)

        self.layered_graph = LayeredGraph()
        self.layered_graph.add(self.h_layout_box)

    def test___init__(self):

        self.assertEqual(
            1, len(self.layered_graph.components)
        )
        self.assertEqual(
            1, len(self.layered_graph.components[0].components)
        )
        self.assertEqual(
            4, len(self.layered_graph.components[0].components[0].components)
        )

    def test_get_connections(self):

        connections = self.layered_graph.get_connections()
        self.assertListEqual([], connections)
