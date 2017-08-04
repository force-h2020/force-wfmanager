import unittest

from force_wfmanager.central_pane.pareto_front import ParetoFront


class ParetoFrontTest(unittest.TestCase):
    def setUp(self):
        self.pareto_front = ParetoFront()

    def test_pareto_front_init(self):
        self.assertEqual(len(self.pareto_front.value_names), 0)
        self.assertEqual(len(self.pareto_front.evaluation_steps), 0)
        self.assertEqual(len(self.pareto_front.data_arrays), 0)
        self.assertIsNone(self.pareto_front.plot)
        self.assertIsNone(self.pareto_front.x)
        self.assertIsNone(self.pareto_front.y)
