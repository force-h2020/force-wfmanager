import unittest
import warnings

from chaco.api import Plot as ChacoPlot

from force_wfmanager.central_pane.analysis_model import AnalysisModel
from force_wfmanager.central_pane.plot import Plot
from traits.api import push_exception_handler
push_exception_handler(reraise_exceptions=True)


class TestPlot(unittest.TestCase):
    def setUp(self):
        self.analysis_model = AnalysisModel()
        self.plot = Plot(analysis_model=self.analysis_model)

    def test_init(self):
        self.assertEqual(len(self.analysis_model.value_names), 0)
        self.assertEqual(len(self.analysis_model.evaluation_steps), 0)
        self.assertEqual(len(self.plot._data_arrays), 0)
        self.assertIsNone(self.plot.x)
        self.assertIsNone(self.plot.y)
        self.assertIsNone(self.plot.update_data_arrays())
        self.plot._update_plot_data()
        self.assertEqual(
            self.plot._plot_data.get_data('x').tolist(), [])
        self.assertEqual(
            self.plot._plot_data.get_data('y').tolist(), [])

    def test_init_data_arrays(self):
        self.analysis_model.value_names = ('density', 'pressure')
        self.assertEqual(self.plot.x, 'density')
        self.assertEqual(self.plot.y, 'pressure')
        self.assertEqual(self.plot._data_arrays, [[], []])

    def test_plot(self):
        self.analysis_model.value_names = ('density', 'pressure')
        self.analysis_model.add_evaluation_step((1.010, 101325))
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.assertIsInstance(self.plot._plot, ChacoPlot)

    def test_push_new_evaluation_steps(self):
        self.analysis_model.value_names = ('density', 'pressure')
        self.analysis_model.add_evaluation_step((1.010, 101325))
        self.analysis_model.add_evaluation_step((1.100, 101423))

        self.assertEqual(len(self.plot._data_arrays), 2)

        first_data_array = self.plot._data_arrays[0]
        second_data_array = self.plot._data_arrays[1]

        self.assertEqual(first_data_array, [1.010, 1.100])
        self.assertEqual(second_data_array, [101325, 101423])

        # Append only one evaluation step
        self.analysis_model.add_evaluation_step((1.123, 102000))

        self.assertEqual(first_data_array, [1.010, 1.100, 1.123])
        self.assertEqual(second_data_array, [101325, 101423, 102000])

        # Append two evaluation steps at the same time
        self.analysis_model.add_evaluation_step((1.156, 102123))
        self.analysis_model.add_evaluation_step((1.242, 102453))

        self.assertEqual(
            first_data_array, [1.010, 1.100, 1.123, 1.156, 1.242])
        self.assertEqual(
            second_data_array, [101325, 101423, 102000, 102123, 102453])

    def test_reinitialize_model(self):
        self.analysis_model.value_names = ('density', 'pressure')
        self.analysis_model.add_evaluation_step((1.010, 101325))
        self.analysis_model.add_evaluation_step((1.100, 101423))

        self.assertEqual(len(self.plot._data_arrays), 2)

        first_data_array = self.plot._data_arrays[0]
        second_data_array = self.plot._data_arrays[1]

        self.assertEqual(first_data_array, [1.010, 1.100])
        self.assertEqual(second_data_array, [101325, 101423])

        self.analysis_model.clear_steps()

        self.assertEqual(first_data_array, [])
        self.assertEqual(second_data_array, [])

    def test_select_plot_axis(self):
        self.analysis_model.value_names = ('density', 'pressure')
        self.analysis_model.add_evaluation_step((1.010, 101325))
        self.analysis_model.add_evaluation_step((1.100, 101423))

        self.assertEqual(
            self.plot._plot_data.get_data('x').tolist(),
            [1.010, 1.100]
        )
        self.assertEqual(
            self.plot._plot_data.get_data('y').tolist(),
            [101325, 101423]
        )

        self.plot.x = 'pressure'
        self.plot.y = 'density'

        self.assertEqual(
            self.plot._plot_data.get_data('x').tolist(),
            [101325, 101423]
        )
        self.assertEqual(
            self.plot._plot_data.get_data('y').tolist(),
            [1.010, 1.100]
        )

    def test_remove_value_names(self):
        self.analysis_model.value_names = ('density', 'pressure')
        self.analysis_model.add_evaluation_step((1.010, 101325))
        self.analysis_model.add_evaluation_step((1.100, 101423))

        self.assertEqual(
            self.plot._plot_data.get_data('x').tolist(),
            [1.010, 1.100]
        )
        self.assertEqual(
            self.plot._plot_data.get_data('y').tolist(),
            [101325, 101423]
        )

        self.analysis_model.value_names = ()

        self.assertEqual(
            self.plot._plot_data.get_data('x').tolist(),
            []
        )
        self.assertEqual(
            self.plot._plot_data.get_data('y').tolist(),
            []
        )

    def test_change_in_value_names_size(self):
        self.analysis_model.value_names = ('density', 'pressure')
        self.analysis_model.add_evaluation_step((1.010, 101325))
        self.analysis_model.add_evaluation_step((1.100, 101423))

        self.analysis_model.value_names = ('density', )

        self.assertEqual(len(self.plot._data_arrays), 1)
        self.assertEqual(len(self.plot._data_arrays[0]), 0)

    def test_selection(self):
        self.analysis_model.value_names = ('density', 'pressure')
        self.analysis_model.add_evaluation_step((1.010, 101325))
        self.analysis_model.add_evaluation_step((1.100, 101423))
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.assertIsInstance(self.plot._plot, ChacoPlot)

        plot_metadata = self.plot._plot_index_datasource.metadata

        # From plot to the model
        plot_metadata['selections'] = [1]
        self.assertEqual(self.analysis_model.selected_step_index, 1)

        plot_metadata['selections'] = [0]
        self.assertEqual(self.analysis_model.selected_step_index, 0)

        plot_metadata['selections'] = []
        self.assertIsNone(self.analysis_model.selected_step_index)

        # From model to the plot
        self.analysis_model.selected_step_index = 1
        self.assertEqual(plot_metadata['selections'], [1])

        self.analysis_model.selected_step_index = None
        self.assertEqual(plot_metadata['selections'], [])

    def test_resize_plot(self):

        # No data
        result = self.plot.resize_plot()
        self.assertIsNone(result)
        self.assertFalse(self.plot._get_reset_enabled())

        # One data point
        self.analysis_model.value_names = ('x', 'y')
        self.analysis_model.add_evaluation_step((2, 3))
        result = self.plot.resize_plot()
        self.assertIsNone(result)
        self.assertFalse(self.plot._get_reset_enabled())

        # More than 1 data point
        self.analysis_model.add_evaluation_step((3, 4))
        result = self.plot.resize_plot()
        self.assertEqual(result, (1.9, 3.1, 2.9, 4.1))
        self.assertTrue(self.plot._get_reset_enabled())
