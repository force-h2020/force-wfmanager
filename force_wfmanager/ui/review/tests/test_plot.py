import mock
import unittest
import warnings

from chaco.api import Plot as ChacoPlot
from chaco.api import ColormappedScatterPlot, ScatterPlot
from chaco.abstract_colormap import AbstractColormap
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from traits.api import push_exception_handler, TraitError
from traits.testing.api import UnittestTools

from force_wfmanager.model.analysis_model import AnalysisModel
from force_wfmanager.ui.review.plot import BasePlot, Plot

push_exception_handler(reraise_exceptions=True)


class TestBasePlot(GuiTestAssistant, unittest.TestCase, UnittestTools):
    def setUp(self):
        super().setUp()
        self.analysis_model = AnalysisModel()
        self.plot = BasePlot(analysis_model=self.analysis_model)

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
        self.plot._check_scheduled_updates()

    def test_init(self):
        self.assertEqual(len(self.analysis_model.header), 0)
        self.assertEqual(len(self.analysis_model.evaluation_steps), 0)
        self.assertEqual("", self.plot.x)
        self.assertEqual("", self.plot.y)
        self.plot._update_plot()
        self.assertEqual(self.plot._plot_data.get_data("x").tolist(), [])
        self.assertEqual(self.plot._plot_data.get_data("y").tolist(), [])
        self.assertTrue(self.plot.plot_updater.active)
        self.assertTrue(self.plot.toggle_automatic_update)

    def test_plot(self):
        self.analysis_model.header = ("density", "pressure")
        self.analysis_model.notify((1.010, 101325))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertIsInstance(self.plot._plot, ChacoPlot)
            self.assertIsInstance(self.plot._axis, ScatterPlot)

    def test_plot_mixed_data(self):
        self.analysis_model.header = ("1", "2", "str")
        self.analysis_model.notify((1, 2, "string"))
        self.check_update_is_requested_and_apply()
        self.assertEqual("1", self.plot.x)
        self.assertEqual("2", self.plot.y)
        self.assertListEqual(self.plot.displayable_value_names, ["1", "2"])
        self.assertEqual(self.plot._plot_data.get_data("x").tolist(), [1])
        self.assertEqual(self.plot._plot_data.get_data("y").tolist(), [2])

        self.analysis_model.notify((3, 4, "another string"))
        self.check_update_is_requested_and_apply()
        self.assertEqual("1", self.plot.x)
        self.assertEqual("2", self.plot.y)
        self.assertListEqual(self.plot.displayable_value_names, ["1", "2"])
        self.assertEqual(self.plot._plot_data.get_data("x").tolist(), [1, 3])
        self.assertEqual(self.plot._plot_data.get_data("y").tolist(), [2, 4])

        self.analysis_model.notify((5, "unexpected string", 6))
        self.check_update_is_requested_and_apply()
        self.assertEqual("1", self.plot.x)
        self.assertEqual("1", self.plot.y)

        self.analysis_model.notify(("oops", 1, 2))
        self.check_update_is_requested_and_apply()
        self.assertEqual("", self.plot.x)
        self.assertEqual("", self.plot.y)

    def test_plot_updater(self):
        self.assertTrue(self.plot.plot_updater.active)

        with mock.patch(
            "force_wfmanager.ui.review.plot."
            + self.plot.__class__.__name__
            + "._update_plot"
        ) as mock_update_plot:
            with self.event_loop_until_condition(
                lambda: not self.plot.update_required
            ):
                self.analysis_model.header = ("density", "pressure")
                self.analysis_model.notify((1.010, 101325))

            mock_update_plot.assert_called()

    def test_check_scheduled_updates(self):
        with mock.patch(
            "force_wfmanager.ui.review.plot."
            + self.plot.__class__.__name__
            + "._update_plot"
        ) as mock_update_plot:
            self.plot.update_required = False
            self.plot._check_scheduled_updates()
            mock_update_plot.assert_not_called()

            self.plot.update_required = True
            self.plot._check_scheduled_updates()
            mock_update_plot.assert_called()
            self.assertFalse(self.plot.update_required)

    def test_push_new_evaluation_steps(self):
        self.analysis_model.header = ("density", "pressure")
        self.analysis_model.notify((1.010, 101325))
        self.analysis_model.notify((1.100, 101423))
        self.check_update_is_requested_and_apply()
        first_data_array = list(self.plot._plot_data.get_data("x"))
        second_data_array = list(self.plot._plot_data.get_data("y"))
        self.assertListEqual(first_data_array, [1.010, 1.100])
        self.assertListEqual(second_data_array, [101325, 101423])

        # Append only one evaluation step
        self.analysis_model.notify((1.123, 102000))
        self.check_update_is_requested_and_apply()
        first_data_array = list(self.plot._plot_data.get_data("x"))
        second_data_array = list(self.plot._plot_data.get_data("y"))
        self.assertListEqual(first_data_array, [1.010, 1.100, 1.123])
        self.assertListEqual(second_data_array, [101325, 101423, 102000])

        # Append two evaluation steps at the same time
        self.analysis_model.notify((1.156, 102123))
        self.analysis_model.notify((1.242, 102453))
        self.check_update_is_requested_and_apply()
        first_data_array = list(self.plot._plot_data.get_data("x"))
        second_data_array = list(self.plot._plot_data.get_data("y"))
        self.assertListEqual(
            first_data_array, [1.010, 1.100, 1.123, 1.156, 1.242]
        )
        self.assertListEqual(
            second_data_array, [101325, 101423, 102000, 102123, 102453]
        )

    def test_reinitialize_model(self):
        self.analysis_model.header = ("density", "pressure")
        self.analysis_model.notify((1.01, 101325))
        self.analysis_model.notify((1.10, 101423))
        self.check_update_is_requested_and_apply()

        first_data_array = list(self.plot._plot_data.get_data("x"))
        second_data_array = list(self.plot._plot_data.get_data("y"))
        self.assertListEqual(first_data_array, [1.01, 1.10])
        self.assertListEqual(second_data_array, [101325, 101423])

        self.analysis_model.clear_steps()
        self.check_update_is_requested_and_apply()
        first_data_array = list(self.plot._plot_data.get_data("x"))
        second_data_array = list(self.plot._plot_data.get_data("y"))
        self.assertEqual([], first_data_array)
        self.assertEqual([], second_data_array)

    def test_select_plot_axis(self):
        self.plot.toggle_automatic_update = False
        self.analysis_model.header = ("a", "b", "c", "d")
        self.analysis_model.notify((1.0, 2.0, 3.0, 4.0))
        self.check_update_is_requested_and_apply()
        self.assertEqual(self.plot._plot_data.get_data("x").tolist(), [1.0])
        self.assertEqual(self.plot._plot_data.get_data("y").tolist(), [2.0])
        self.assertEqual((0.5, 1.5, 1.5, 2.5), self.plot._get_plot_range())

        self.analysis_model.notify((5.0, 4.0, 3.0, 2.0))
        self.check_update_is_requested_and_apply()
        self.assertEqual(
            self.plot._plot_data.get_data("x").tolist(), [1.0, 5.0]
        )
        self.assertEqual(
            self.plot._plot_data.get_data("y").tolist(), [2.0, 4.0]
        )
        self.assertEqual((0.5, 1.5, 1.5, 2.5), self.plot._get_plot_range())

        self.plot.x = "b"
        self.assertEqual(
            self.plot._plot_data.get_data("x").tolist(), [2.0, 4.0]
        )
        self.assertEqual(
            self.plot._plot_data.get_data("y").tolist(), [2.0, 4.0]
        )
        self.assertEqual(
            (2.0 - 0.1 * (4.0 - 2.0), 4.0 + 0.1 * (4.0 - 2.0), 1.5, 2.5),
            self.plot._get_plot_range(),
        )

        self.plot.y = "a"
        self.assertEqual(
            self.plot._plot_data.get_data("x").tolist(), [2.0, 4.0]
        )
        self.assertEqual(
            self.plot._plot_data.get_data("y").tolist(), [1.0, 5.0]
        )
        self.assertEqual(
            (
                2.0 - 0.1 * (4.0 - 2.0),
                4.0 + 0.1 * (4.0 - 2.0),
                1.0 - 0.1 * (5.0 - 1.0),
                5.0 + 0.1 * (5.0 - 1.0),
            ),
            self.plot._get_plot_range(),
        )

        with mock.patch(
            "force_wfmanager.ui.review.plot."
            + self.plot.__class__.__name__
            + "._update_plot_y_data"
        ) as mock_update_plot_y_data, mock.patch(
            "force_wfmanager.ui.review.plot."
            + self.plot.__class__.__name__
            + ".recenter_y_axis"
        ) as mock_recenter_y_axis:
            self.plot.y = "c"
            mock_update_plot_y_data.assert_called()
            mock_recenter_y_axis.assert_called()

        self.plot.toggle_automatic_update = True
        with mock.patch(
            "force_wfmanager.ui.review.plot.BasePlot._update_plot"
        ) as mock_update:
            self.plot._update_plot()
            mock_update.assert_called()

        self.plot._update_plot()
        self.assertEqual((1.8, 4.2, 2.5, 3.5), self.plot._get_plot_range())

    def test_remove_value_names(self):
        self.analysis_model.header = ("density", "pressure")
        self.analysis_model.notify((1.010, 101325))
        self.analysis_model.notify((1.100, 101423))
        self.check_update_is_requested_and_apply()

        self.assertEqual(
            self.plot._plot_data.get_data("x").tolist(), [1.010, 1.100]
        )
        self.assertEqual(
            self.plot._plot_data.get_data("y").tolist(), [101325, 101423]
        )

        self.analysis_model.clear()
        self.check_update_is_requested_and_apply()

        self.assertEqual([], self.plot._plot_data.get_data("x").tolist())
        self.assertEqual([], self.plot._plot_data.get_data("y").tolist())

    def test_selection(self):
        self.analysis_model.header = ("density", "pressure")
        self.analysis_model.notify((1.010, 101325))
        self.analysis_model.notify((1.100, 101423))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertIsInstance(self.plot._plot, ChacoPlot)

        plot_metadata = self.plot._plot_index_datasource.metadata

        # From plot to the model
        plot_metadata["selections"] = [1]
        self.assertEqual(self.analysis_model.selected_step_indices, [1])

        plot_metadata["selections"] = [0]
        self.assertEqual(self.analysis_model.selected_step_indices, [0])

        plot_metadata["selections"] = []
        self.assertIsNone(self.analysis_model.selected_step_indices)

        # From model to the plot
        self.analysis_model.selected_step_indices = [1]
        self.assertEqual(plot_metadata["selections"], [1])

        self.analysis_model.selected_step_indices = None
        self.assertEqual(plot_metadata["selections"], [])

    def test_recenter_plot(self):

        # No data
        result = self.plot.recenter_plot()
        self.assertEqual((-1, 1, -1, 1), result)
        self.assertFalse(self.plot._get_reset_enabled())

        # One data point
        self.analysis_model.header = ("x", "y")
        self.analysis_model.notify((2, 3))
        self.check_update_is_requested_and_apply()
        committed_range = self.plot.recenter_plot()
        self.assertEqual((1.5, 2.5, 2.5, 3.5), committed_range)
        actual_range = self.plot._get_plot_range()
        self.assertEqual(actual_range, committed_range)
        self.assertTrue(self.plot._get_reset_enabled())

        # More than 1 data point
        self.analysis_model.notify((3, 4))
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

    def test_calculate_axis_bounds(self):
        data = [1.0]
        self.assertEqual((0.5, 1.5), self.plot.calculate_axis_bounds(data))
        data = []
        self.assertEqual((-1.0, 1.0), self.plot.calculate_axis_bounds(data))
        data = [1.0, 2.0, 3.0]
        self.assertEqual(
            (1.0 - 0.1 * (3.0 - 1.0), 3.0 + 0.1 * (3.0 - 1.0)),
            self.plot.calculate_axis_bounds(data),
        )


class TestPlot(TestBasePlot):
    def setUp(self):
        super().setUp()
        self.plot = Plot(analysis_model=self.analysis_model)

    def test_cmapped_plot(self):
        self.analysis_model.header = ("density", "pressure", "color")
        self.analysis_model.notify((1.010, 101325, 1))
        self.check_update_is_requested_and_apply()
        self.plot.color_plot = True
        self.plot.color_by = "color"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertEqual(self.plot.color_by, "color")
            self.assertIsInstance(self.plot._plot, ChacoPlot)
            self.assertIsInstance(self.plot._axis, ColormappedScatterPlot)
            self.assertIsInstance(
                self.plot._axis.color_mapper, AbstractColormap
            )
            old_cmap = self.plot._axis.color_mapper
            self.plot.colormap = "seismic"
            self.assertIsInstance(
                self.plot._axis.color_mapper, AbstractColormap
            )
            self.assertNotEqual(old_cmap, self.plot._axis.color_mapper)
            self.assertEqual(
                old_cmap.range, self.plot._axis.color_mapper.range
            )

        with self.assertRaises(TraitError):
            self.plot.colormap = "not_viridis"

        self.plot.colormap = "viridis"
        self.plot.colormap = "CoolWarm"

        self.plot.color_plot = False
        self.assertIsInstance(self.plot._axis, ScatterPlot)

    def test_ranges_are_kept(self):
        self.analysis_model.header = ("density", "pressure", "color")
        self.analysis_model.notify((1.010, 101325, 1))
        self.check_update_is_requested_and_apply()
        self.plot._set_plot_range(0.5, 2, 100000, 103000)
        self.plot.color_plot = True
        self.plot.color_by = "color"
        self.assertEqual(self.plot._get_plot_range(), (0.5, 2, 100000, 103000))
        self.assertEqual(self.plot._plot.x_axis.title, "density")
        self.assertEqual(self.plot._plot.y_axis.title, "pressure")
