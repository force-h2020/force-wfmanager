import mock
import time
import warnings

from chaco.api import Plot as ChacoPlot
from chaco.api import BaseXYPlot

from force_wfmanager.model.analysis_model import AnalysisModel
from traits.api import push_exception_handler

push_exception_handler(reraise_exceptions=True)


class PlotBaseTestCase:

    def setUp(self):
        self.analysis_model = AnalysisModel()
        self.plot = None
        self.path = ''

    def check_update_is_requested_and_apply(self):
        """ Check that a plot update is requested (scheduled for the next
        cycle of the timer) and that the timer is active, which means the
        updates are going to happen.
        Once that is assured, do the updates immediately instead of waiting
        one cycle (that would slow down the test)
        """
        # check
        self.assertTrue(self.plot.update_required)
        self.assertTrue(self.plot.plot_updater.active)
        # update
        self.plot.update_data_arrays()
        self.plot._update_plot()
        self.plot.update_required = False

    def test_init(self):
        self.assertEqual(len(self.analysis_model.value_names), 0)
        self.assertEqual(len(self.analysis_model.evaluation_steps), 0)
        self.assertEqual(len(self.plot._data_arrays), 0)
        self.assertIsNone(self.plot.x)
        self.assertIsNone(self.plot.y)
        self.assertIsNone(self.plot.update_data_arrays())
        self.plot._update_plot()
        self.assertEqual(
            self.plot._plot_data.get_data('x').tolist(), [])
        self.assertEqual(
            self.plot._plot_data.get_data('y').tolist(), [])
        self.assertTrue(self.plot.plot_updater.active)

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
            self.assertIsInstance(self.plot._axis, BaseXYPlot)

    def test_plot_updater(self):
        self.assertTrue(self.plot.plot_updater.active)
        with mock.patch(self.path) as mock_update_plot:
            self.assertFalse(self.plot.update_required)

            # check that after a cycle no update is done
            time.sleep(1.1)
            mock_update_plot.assert_not_called()

            self.analysis_model.value_names = ('density', 'pressure')
            self.analysis_model.add_evaluation_step((1.010, 101325))
            self.analysis_model.add_evaluation_step((1.100, 101423))
            self.assertTrue(self.plot.update_required)

            # wait a cycle for the update
            time.sleep(1.1)
            mock_update_plot.assert_called()

    def test_check_scheduled_updates(self):
        with mock.patch(self.path) as mock_update_plot:
            self.assertFalse(self.plot.update_required)
            self.plot._check_scheduled_updates()
            mock_update_plot.assert_not_called()

            self.plot.update_required = True
            self.plot._check_scheduled_updates()
            mock_update_plot.assert_called()
            self.assertFalse(self.plot.update_required)

    def test_push_new_evaluation_steps(self):
        self.assertFalse(self.plot.update_required)

        self.analysis_model.value_names = ('density', 'pressure')
        self.analysis_model.add_evaluation_step((1.010, 101325))
        self.analysis_model.add_evaluation_step((1.100, 101423))

        self.check_update_is_requested_and_apply()

        self.assertEqual(len(self.plot._data_arrays), 2)

        first_data_array = self.plot._data_arrays[0]
        second_data_array = self.plot._data_arrays[1]

        self.assertEqual(first_data_array, [1.010, 1.100])
        self.assertEqual(second_data_array, [101325, 101423])

        # Append only one evaluation step
        self.analysis_model.add_evaluation_step((1.123, 102000))

        self.check_update_is_requested_and_apply()

        self.assertEqual(first_data_array, [1.010, 1.100, 1.123])
        self.assertEqual(second_data_array, [101325, 101423, 102000])

        # Append two evaluation steps at the same time
        self.analysis_model.add_evaluation_step((1.156, 102123))
        self.analysis_model.add_evaluation_step((1.242, 102453))

        self.check_update_is_requested_and_apply()

        self.assertEqual(
            first_data_array, [1.010, 1.100, 1.123, 1.156, 1.242])
        self.assertEqual(
            second_data_array, [101325, 101423, 102000, 102123, 102453])

    def test_reinitialize_model(self):
        self.analysis_model.value_names = ('density', 'pressure')
        self.analysis_model.add_evaluation_step((1.010, 101325))
        self.analysis_model.add_evaluation_step((1.100, 101423))
        self.check_update_is_requested_and_apply()

        self.assertEqual(len(self.plot._data_arrays), 2)

        first_data_array = self.plot._data_arrays[0]
        second_data_array = self.plot._data_arrays[1]

        self.assertEqual(first_data_array, [1.010, 1.100])
        self.assertEqual(second_data_array, [101325, 101423])

        self.analysis_model.clear_steps()
        self.check_update_is_requested_and_apply()

        self.assertEqual(first_data_array, [])
        self.assertEqual(second_data_array, [])

    def test_select_plot_axis(self):
        self.analysis_model.value_names = ('density', 'pressure')
        self.analysis_model.add_evaluation_step((1.010, 101325))
        self.analysis_model.add_evaluation_step((1.100, 101423))
        self.check_update_is_requested_and_apply()

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
        self.check_update_is_requested_and_apply()

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
        self.assertEqual(self.analysis_model.selected_step_indices, [1])

        plot_metadata['selections'] = [0]
        self.assertEqual(self.analysis_model.selected_step_indices, [0])

        plot_metadata['selections'] = []
        self.assertIsNone(self.analysis_model.selected_step_indices)

        # From model to the plot
        self.analysis_model.selected_step_indices = [1]
        self.assertEqual(plot_metadata['selections'], [1])

        self.analysis_model.selected_step_indices = None
        self.assertEqual(plot_metadata['selections'], [])

    def test_recenter_plot(self):

        # No data
        result = self.plot.recenter_plot()
        self.assertIsNone(result)
        self.assertFalse(self.plot._get_reset_enabled())

        # One data point
        self.analysis_model.value_names = ('x', 'y')
        self.analysis_model.add_evaluation_step((2, 3))
        self.check_update_is_requested_and_apply()
        committed_range = self.plot.recenter_plot()
        actual_range = self.plot._get_plot_range()
        self.assertEqual(committed_range, (1.5, 2.5, 2.5, 3.5))
        self.assertEqual(committed_range, actual_range)
        self.assertTrue(self.plot._get_reset_enabled())

        # More than 1 data point
        self.analysis_model.add_evaluation_step((3, 4))
        self.check_update_is_requested_and_apply()
        self.plot.recenter_plot()
        committed_range = self.plot.recenter_plot()
        actual_range = self.plot._get_plot_range()
        self.assertEqual(committed_range, (1.9, 3.1, 2.9, 4.1))
        self.assertEqual(committed_range, actual_range)
        self.assertTrue(self.plot._get_reset_enabled())
        self.plot._plot.range2d.x_range.low = -10
        self.plot.reset_plot = True
        self.assertEqual(self.plot._plot.range2d.x_range.low, 1.9)
