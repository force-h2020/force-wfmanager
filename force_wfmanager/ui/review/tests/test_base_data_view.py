from unittest import TestCase
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from traits.testing.api import UnittestTools

from force_wfmanager.ui.review.base_data_view import BaseDataView
from force_wfmanager.model.analysis_model import AnalysisModel


class TestBaseDataView(GuiTestAssistant, TestCase, UnittestTools):
    def setUp(self):
        super().setUp()
        self.analysis_model = AnalysisModel()
        self.plot = BaseDataView(analysis_model=self.analysis_model)

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
