import unittest
from functools import partial

from pyface.ui.qt4.util.modal_dialog_tester import ModalDialogTester
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant

from force_wfmanager.tests.dummy_classes import DummyContributedUI2
from force_wfmanager.ui import ContributedUIHandler


class TestContributedUI(GuiTestAssistant, unittest.TestCase):

    def setUp(self):
        self.ui = DummyContributedUI2()
        super().setUp()

    def test_buttons_exist(self):
        tester = ModalDialogTester(partial(
            self.ui.edit_traits, kind="modal", handler=ContributedUIHandler()
        ))
        tester.open_and_run(
            when_opened=lambda x: x.click_widget("Run Workflow")
        )
        tester.open_and_run(
            when_opened=lambda x: x.click_widget("Update Workflow")
        )

    def test_required_plugins(self):
        expected = {"force.bdss.enthought.plugin.uitest.v2": 2}
        self.assertDictEqual(expected, self.ui.required_plugins)
