import unittest

from force_wfmanager.central_pane.analysis import Result, EvaluationStep


class AnalysisTest(unittest.TestCase):
    def test_result(self):
        result = Result(name='x', value=0.2)

        self.assertEqual(result.name, 'x')
        self.assertEqual(result.value, 0.2)

        result.value = 'string_value'

        self.assertEqual(result.value, 'string_value')

    def test_evaluation_step(self):
        ev = EvaluationStep(results=[
            Result(name='x', value=0.2),
            Result(name='y', value=1.1),
            Result(name='z', value=2.0),
        ])

        self.assertEqual(len(ev.results), 3)

    def test_step(self):
        ev1 = EvaluationStep()
        ev2 = EvaluationStep()

        EvaluationStep.init_step_count()

        ev3 = EvaluationStep()

        self.assertEqual(ev1.step, 1)
        self.assertEqual(ev2.step, 2)
        self.assertEqual(ev3.step, 1)

    def tearDown(self):
        EvaluationStep.init_step_count()
