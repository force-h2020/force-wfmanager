import unittest

from force_wfmanager.central_pane.result_table import (
    ResultTable, EvaluationStep, Result
)


def create_evaluation_step(results=[]):
    return EvaluationStep(results=results)


class EvaluationStepTest(unittest.TestCase):
    def test_init(self):
        self.assertEqual(EvaluationStep._step, 0)

    def test_step_count(self):
        self.assertEqual(EvaluationStep._step, 0)

        ev = create_evaluation_step()

        self.assertEqual(ev.step, 1)
        self.assertEqual(EvaluationStep._step, 1)

        EvaluationStep.init_step_count()

        self.assertEqual(EvaluationStep._step, 0)

    def tearDown(self):
        EvaluationStep.init_step_count()


class ResultTableTest(unittest.TestCase):
    def setUp(self):
        self.ev1 = create_evaluation_step([
            Result(name='x', value=0.2),
            Result(name='y', value=2),
            Result(name='z', value=20),
            Result(name='foo', value='bar'),
        ])
        self.ev2 = create_evaluation_step([
            Result(name='x', value=0.3),
            Result(name='y', value=3),
            Result(name='z', value=30),
            Result(name='bar', value='baz'),
        ])
        self.table = ResultTable()

    def test_table_init(self):
        self.assertEqual(self.table.column_names, ['step'])
        self.assertEqual(len(self.table.columns), 1)
        self.assertEqual(len(self.table.evaluation_steps), 0)

    def test_append_evaluation_step(self):
        self.table.append_evaluation_step(self.ev1)
        self.assertEqual(
            self.table.column_names,
            ['step', 'x', 'y', 'z', 'foo']
        )
        self.assertEqual(len(self.table.columns), 5)
        self.assertEqual(len(self.table.evaluation_steps), 1)

        self.table.append_evaluation_step(self.ev2)
        self.assertEqual(
            self.table.column_names,
            ['step', 'x', 'y', 'z', 'foo', 'bar']
        )
        self.assertEqual(len(self.table.columns), 6)
        self.assertEqual(len(self.table.evaluation_steps), 2)

    def test_get_table_value(self):
        self.table.append_evaluation_step(self.ev1)
        self.assertEqual(self.table.columns[0].get_value(self.ev1), '1')
        self.assertEqual(self.table.columns[1].get_value(self.ev1), '0.2')
        self.assertEqual(self.table.columns[4].get_value(self.ev1), 'bar')

        self.table.append_evaluation_step(self.ev2)
        self.assertEqual(self.table.columns[0].get_value(self.ev2), '2')
        self.assertEqual(self.table.columns[1].get_value(self.ev2), '0.3')
        self.assertEqual(self.table.columns[4].get_value(self.ev2), None)

    def test_clear_table(self):
        self.table.append_evaluation_step(self.ev1)
        self.table.append_evaluation_step(self.ev2)

        self.table.clear_table()

        self.assertEqual(self.table.column_names, ['step'])
        self.assertEqual(len(self.table.columns), 1)
        self.assertEqual(len(self.table.evaluation_steps), 0)
        self.assertEqual(EvaluationStep._step, 0)


    def tearDown(self):
        EvaluationStep.init_step_count()
