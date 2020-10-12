#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

from unittest import TestCase, mock
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from traits.testing.api import UnittestTools

from force_wfmanager.ui.review.base_data_view import BaseDataView
from force_wfmanager.model.analysis_model import AnalysisModel


class BasePlotTestCase(GuiTestAssistant, TestCase, UnittestTools):

    plot_cls = BaseDataView

    def setUp(self):
        super().setUp()
        self.analysis_model = AnalysisModel()
        self.plot = self.plot_cls(analysis_model=self.analysis_model)
        self.mock_path = '.'.join(
            [self.plot.__class__.__module__,
             self.plot.__class__.__name__]
        )

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


class TestBaseDataView(BasePlotTestCase):

    def test_initialize(self):
        self.assertFalse(self.plot.is_active_view)

    def test_displayable_mask(self):
        self.assertTrue(self.plot.displayable_data_mask(1))
        self.assertTrue(self.plot.displayable_data_mask(42.0))
        self.assertFalse(self.plot.displayable_data_mask(None))

        another_plot = BaseDataView(
            analysis_model=self.analysis_model,
            displayable_data_mask=lambda object: isinstance(object, str),
        )
        self.assertTrue(another_plot.displayable_data_mask("string"))
        self.assertFalse(another_plot.displayable_data_mask(1))

    def test__update_displayable_value_names(self):
        self.plot._update_displayable_value_names()
        self.assertEqual([], self.plot.displayable_value_names)

        self.analysis_model.header = ("1", "2", "str")
        self.analysis_model.notify((1, 2, "string"))
        self.plot._update_displayable_value_names()
        self.assertListEqual(self.plot.displayable_value_names, ["1", "2"])

        self.analysis_model.notify((3, 4, "another string"))
        self.plot._update_displayable_value_names()
        self.assertListEqual(self.plot.displayable_value_names, ["1", "2"])

        self.analysis_model.notify((5, "unexpected string", 6))
        self.plot._update_displayable_value_names()
        self.assertListEqual(self.plot.displayable_value_names, ["1"])

        self.analysis_model.notify(("oops", 1, 2))
        self.plot._update_displayable_value_names()
        self.assertListEqual(self.plot.displayable_value_names, [])

    def test_plot_updater(self):
        self.assertTrue(self.plot.plot_updater.active)

        with mock.patch(
            self.mock_path + ".update_data_view"
        ) as mock_update_plot:
            with self.event_loop_until_condition(
                lambda: not self.plot.update_required
            ):
                self.analysis_model.header = ("density", "pressure")
                self.analysis_model.notify((1.010, 101325))

            mock_update_plot.assert_called()

    def test_check_scheduled_updates(self):
        with mock.patch(
            self.mock_path + ".update_data_view"
        ) as mock_update_data_view, mock.patch(
            self.mock_path + "._update_displayable_value_names"
        ) as mock_update_value_names:
            self.plot.update_required = False
            self.plot._check_scheduled_updates()
            mock_update_data_view.assert_not_called()
            mock_update_value_names.assert_not_called()

            self.plot.update_required = True
            self.plot._check_scheduled_updates()
            mock_update_data_view.assert_called()
            mock_update_value_names.assert_called()
            self.assertFalse(self.plot.update_required)
