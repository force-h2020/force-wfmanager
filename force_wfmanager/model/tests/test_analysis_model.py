from unittest import mock, TestCase

from traits.trait_errors import TraitError

from force_wfmanager.model.analysis_model import AnalysisModel


class TestAnalysisModel(TestCase):
    def setUp(self):
        self.analysis = AnalysisModel()

    def test_analysis_init(self):
        self.assertEqual(len(self.analysis.value_names), 0)
        self.assertEqual(len(self.analysis.evaluation_steps), 0)
        self.assertEqual(self.analysis.selected_step_indices, None)

    def test_add_evaluation_step(self):
        self.analysis.value_names = ('foo', 'bar')

        with self.assertRaises(ValueError):
            self.analysis.add_evaluation_step((1, 2, 3))

        with self.assertRaises(TraitError):
            self.analysis.add_evaluation_step("12")

        self.analysis.value_names = ()

        with self.assertRaises(ValueError):
            self.analysis.add_evaluation_step(())

    def test_change_selection(self):
        self.analysis.value_names = ['foo', 'bar']
        self.analysis.add_evaluation_step((1, 2))
        self.analysis.add_evaluation_step((3, 4))
        self.analysis.add_evaluation_step((5, 6))

        self.analysis.selected_step_indices = [0]
        self.analysis.selected_step_indices = [2]
        self.analysis.selected_step_indices = None

        with self.assertRaises(TraitError):
            self.analysis.selected_step_indices = 1

        with self.assertRaises(ValueError):
            self.analysis.selected_step_indices = [3]

        with self.assertRaises(TraitError):
            self.analysis.selected_step_indices = [3.0]

        with self.assertRaises(ValueError):
            self.analysis.selected_step_indices = [-1]

        with self.assertRaises(TraitError):
            self.analysis.selected_step_indices = "hello"

        with self.assertRaises(TraitError):
            self.analysis.selected_step_indices = ["hello"]

        self.analysis.value_names = ('bar', 'baz')
        self.assertEqual(self.analysis.selected_step_indices, None)
        self.assertEqual(self.analysis.evaluation_steps, [])

    def test_clear(self):
        self.analysis.value_names = ('foo', 'bar')
        self.analysis.add_evaluation_step((1, 2))
        self.analysis.add_evaluation_step((3, 4))
        self.analysis.add_evaluation_step((5, 6))
        self.analysis.selected_step_indices = [0]
        self.analysis.selected_step_indices = [0, 1, 2]
        self.analysis.selected_step_indices = [0, 2]

        with self.assertRaises(ValueError):
            self.analysis.selected_step_indices = [0, 3]
        with self.assertRaises(ValueError):
            self.analysis.selected_step_indices = [5, 6]

        with self.assertRaises(TraitError):
            self.analysis.selected_step_indices = 0

        self.analysis.clear()

        self.assertEqual(self.analysis.value_names, ())
        self.assertEqual(self.analysis.evaluation_steps, [])
        self.assertEqual(self.analysis.selected_step_indices, None)

    def test_as_json(self):
        self.analysis.value_names = ('foo', 'bar', 'label')
        self.analysis.add_evaluation_step((1, 2, 'x'))
        self.analysis.add_evaluation_step((3, 4, 'y'))
        self.analysis.add_evaluation_step((5, 6, 'z'))
        json_rep = {'foo': [1, 3, 5],
                    'bar': [2, 4, 6],
                    'label': ['x', 'y', 'z']}

        self.assertEqual(self.analysis.as_json(), json_rep)

    def test_from_dict(self):
        json_rep = {'foo': [1, 3, 5],
                    'bar': [2, 4, 6],
                    'label': ['x', 'y', 'z']}
        self.analysis.value_names = ('notfoo', 'notbar', 'notlabel')

        self.analysis.add_evaluation_step((11, 22, 'xx'))
        self.analysis.add_evaluation_step((55, 66, 'zz'))

        self.analysis.from_dict(json_rep)
        self.assertEqual(self.analysis.value_names, ('foo', 'bar', 'label'))
        self.assertEqual(len(self.analysis.evaluation_steps), 3)
        self.assertEqual(self.analysis.evaluation_steps[0], (1, 2, 'x'))
        self.assertEqual(self.analysis.evaluation_steps[1], (3, 4, 'y'))
        self.assertEqual(self.analysis.evaluation_steps[2], (5, 6, 'z'))

    def test_write_to_json(self):
        json_rep = {'foo': [1, 3, 5],
                    'bar': [2, 4, 6],
                    'label': ['x', 'y', 'z']}
        self.analysis.from_dict(json_rep)
        self.assertEqual(self.analysis.as_json(), json_rep)
        mock_open = mock.mock_open()
        with mock.patch('__main__.open', mock_open, create=True):
            with mock_open('blah', 'w') as fp:
                success = self.analysis.write_to_json(fp)

        self.assertTrue(success)

    def test_write_to_csv(self):
        json_rep = {'foo': [1, 3, 5],
                    'bar': [2, 4, 6],
                    'label': ['x', 'y', 'z']}
        self.analysis.from_dict(json_rep)
        self.assertEqual(self.analysis.as_json(), json_rep)
        mock_open = mock.mock_open()
        with mock.patch('__main__.open', mock_open, create=True):
            with mock_open('blah', 'w') as fp:
                success = self.analysis.write_to_csv(fp)

        self.assertTrue(success)
        handle = mock_open()

        csv_string = ['foo, bar, label\n',
                      '1, 2, x\n',
                      '3, 4, y\n',
                      '5, 6, z\n']

        # unfortunately this doesn't enforce the order of the call
        # but I think this is probably overkill anyway...
        for line in csv_string:
            handle.write.assert_any_call(line)
