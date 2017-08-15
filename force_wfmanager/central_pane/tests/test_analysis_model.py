import unittest

from traits.trait_errors import TraitError

from force_wfmanager.central_pane.analysis_model import AnalysisModel


class AnalysisModelTest(unittest.TestCase):
    def setUp(self):
        self.analysis = AnalysisModel()

    def test_analysis_init(self):
        self.assertEqual(len(self.analysis.value_names), 0)
        self.assertEqual(len(self.analysis.evaluation_steps), 0)
        self.assertEqual(self.analysis.selected_step_index, None)

    def test_add_evaluation_step(self):
        self.analysis.value_names = ['foo', 'bar']

        with self.assertRaises(ValueError):
            self.analysis.add_evaluation_step((1, 2, 3))

        with self.assertRaises(TraitError):
            self.analysis.add_evaluation_step("12")

        self.analysis.value_names = []

        with self.assertRaises(ValueError):
            self.analysis.add_evaluation_step(())

    def test_change_selection(self):
        self.analysis.value_names = ['foo', 'bar']
        self.analysis.add_evaluation_step((1, 2))
        self.analysis.add_evaluation_step((3, 4))
        self.analysis.add_evaluation_step((5, 6))

        self.analysis.selected_step_index = 0
        self.analysis.selected_step_index = 2
        self.analysis.selected_step_index = None

        with self.assertRaises(ValueError):
            self.analysis.selected_step_index = 3

        with self.assertRaises(TraitError):
            self.analysis.selected_step_index = 3.0

        with self.assertRaises(ValueError):
            self.analysis.selected_step_index = -1

        with self.assertRaises(TraitError):
            self.analysis.selected_step_index = "hello"

        self.analysis.value_names = ['bar', 'baz']
        self.assertEqual(self.analysis.selected_step_index, None)
        self.assertEqual(self.analysis.evaluation_steps, [])

    def test_clear(self):
        self.analysis.value_names = ['foo', 'bar']
        self.analysis.add_evaluation_step((1, 2))
        self.analysis.add_evaluation_step((3, 4))
        self.analysis.add_evaluation_step((5, 6))
        self.analysis.selected_step_index = 0

        self.analysis.clear()

        self.assertEqual(self.analysis.value_names, [])
        self.assertEqual(self.analysis.evaluation_steps, [])
        self.assertEqual(self.analysis.selected_step_index, None)
