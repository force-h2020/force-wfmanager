from enable.stacked_container import VStackedContainer


class LayeredGraph(VStackedContainer):

    stack_order = 'top_to_bottom'

    def get_connections(self):
        connections = []
        sources = {}

        for component in reversed(self.components):
            base_x, base_y = component.position
            for node in component.components:
                x = base_x + node.x
                y = base_y + node.y

                connections.extend(
                    (sources[input.text], (input, (x, y)))
                    for input in node.inputs
                    if input.text and input.text in sources
                )
            for node in component.components:
                x = base_x + node.x
                y = base_y + node.y

                sources.update(
                    (output.text, (output, (x, y)))
                    for output in node.outputs
                    if output.text
                )

        return connections

    def _draw_overlay(self, gc, view_bounds=None, mode="normal"):
        connections = self.get_connections()
        with gc:
            gc.set_stroke_color((0.0, 0.0, 0.0, 1.0))
            for source, sink in connections:

                source, (x, y) = source
                start_x = x1 = x + (source.x + source.x2)/2
                start_y = y + source.outer_y

                sink, (x, y) = sink
                end_x = x2 = x + (sink.x + sink.x2)/2
                end_y = y + sink.outer_y2

                y1 = y2 = (start_y + end_y)/2

                gc.move_to(start_x, start_y)
                gc.curve_to(x1, y1, x2, y2, end_x, end_y)
                gc.stroke_path()
