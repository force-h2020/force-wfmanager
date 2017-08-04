import unittest

from chaco.api import Plot

from force_wfmanager.central_pane.pareto_front import ParetoFront


class ParetoFrontTest(unittest.TestCase):
    def setUp(self):
        self.pareto_front = ParetoFront()

    def test_init(self):
        self.assertEqual(len(self.pareto_front.value_names), 0)
        self.assertEqual(len(self.pareto_front.evaluation_steps), 0)
        self.assertEqual(len(self.pareto_front.data_arrays), 0)
        self.assertIsNone(self.pareto_front.plot)
        self.assertIsNone(self.pareto_front.x)
        self.assertIsNone(self.pareto_front.y)

    def test_data_arrays(self):
        self.pareto_front.value_names = ['density', 'pressure']
        self.pareto_front.evaluation_steps = [
            (1.010, 101325),
            (1.100, 101423),
            (1.123, 102000),
            (1.156, 102123),
            (1.242, 102453),
        ]

        self.assertEqual(len(self.pareto_front.data_arrays), 2)

        self.assertEqual(len(self.pareto_front.data_arrays[0]), 5)
        self.assertEqual(len(self.pareto_front.data_arrays[1]), 5)

        self.assertEqual(
            self.pareto_front.data_arrays[0],
            [1.010, 1.100, 1.123, 1.156, 1.242]
        )

        self.assertEqual(
            self.pareto_front.data_arrays[1],
            [101325, 101423, 102000, 102123, 102453]
        )

    def test_plot(self):
        self.pareto_front.value_names = ['density', 'pressure']
        self.pareto_front.evaluation_steps = [
            (1.010, 101325),
        ]

        self.assertIsInstance(self.pareto_front.plot, Plot)
