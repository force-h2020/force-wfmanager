import unittest
from functools import partial

from pyface.ui.qt4.util.modal_dialog_tester import ModalDialogTester
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant

from force_wfmanager.tests.dummy_classes.dummy_contributed_ui import (
    DummyContributedUI2
)
from force_wfmanager.ui import ContributedUIHandler
from force_wfmanager.ui.contributed_ui.contributed_ui import search, parse_id


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

    def test_search_for_id(self):
        input_dict = {
            'mco': {
                'id': 'mco_identifier'
            },
            'execution_layers': [
                [
                    {
                        'id': 'datasource_id',
                        'info': [1, 2, 3]
                    },
                    {
                        'id': 'datasource_id2',
                        'info': [4, 5, 6]
                    },

                ],
                [
                    {
                        'id': 'datasource_id3',
                        'info': [7, 8, 9]
                    },
                ]

            ]
        }
        results = search(input_dict, search_term="id")
        expected = [
            'mco_identifier', 'datasource_id', 'datasource_id2',
            'datasource_id3'
        ]
        self.assertListEqual(results, expected)

    def test_parse_id_error(self):
        with self.assertRaisesRegex(ValueError, "Unexpected plugin id:"):
            parse_id("incorrectid")