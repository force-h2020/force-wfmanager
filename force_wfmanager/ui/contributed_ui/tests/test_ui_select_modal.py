import unittest

from force_bdss.tests.dummy_classes.extension_plugin import (
    DummyExtensionPlugin
)
from force_wfmanager.tests.dummy_classes import (
    DummyContributedUI, DummyContributedUI2, DummyUIPlugin
)
from force_wfmanager.ui import UISelectModal, ContributedUI
from force_wfmanager.ui.contributed_ui.ui_select_modal import (
    DESCRIPTION_TEMPLATE
)


class DummyBrokenContributedUI(ContributedUI):

    name = "DummyUI"

    desc = "Dummy Broken UI"

    workflow_data = {
        "mco":
            {"id": "force.bdss.test.plugin.test4.v1300.factory.mco"}
    }


class TestUISelectModal(unittest.TestCase):

    def setUp(self) -> None:
        self.plugins = [DummyExtensionPlugin(), DummyUIPlugin()]

    def test_ui_modal_init(self):
        contributed_ui = DummyContributedUI()
        ui_modal = UISelectModal(
            contributed_uis=[contributed_ui],
            available_plugins=self.plugins
        )
        expected_plugin_info = {
            'force.bdss.enthought.plugin.test.v0': 0,
            'force.bdss.enthought.plugin.uitest.v2': 2
        }
        expected_ui_name_map = {
            'DummyUI': contributed_ui,
        }
        self.assertDictEqual(
            ui_modal.avail_plugin_info, expected_plugin_info
        )
        self.assertDictEqual(
            ui_modal.ui_name_map, expected_ui_name_map
        )

    def test_duplicate_ui_name(self):
        contributed_ui = DummyContributedUI()
        other_contributed_ui = DummyContributedUI2()
        ui_modal = UISelectModal(
            contributed_uis=[contributed_ui, other_contributed_ui],
            available_plugins=self.plugins
        )
        expected_ui_name_map = {
            'DummyUI': contributed_ui, 'DummyUI (2)': other_contributed_ui
        }
        self.assertDictEqual(
            ui_modal.ui_name_map, expected_ui_name_map
        )

    def test_broken_ui_not_shown(self):
        contributed_ui = DummyContributedUI()
        broken_ui = DummyBrokenContributedUI()
        ui_modal = UISelectModal(
            contributed_uis=[contributed_ui, broken_ui],
            available_plugins=self.plugins
        )
        expected_ui_name_map = {
            'DummyUI': contributed_ui
        }
        self.assertDictEqual(
            ui_modal.ui_name_map, expected_ui_name_map
        )

    def test_selected_ui_shows_desc(self):
        contributed_ui = DummyContributedUI()
        other_contributed_ui = DummyContributedUI2()
        ui_modal = UISelectModal(
            contributed_uis=[contributed_ui, other_contributed_ui],
            available_plugins=self.plugins
        )
        ui_modal.selected_ui_name = "DummyUI (2)"
        self.assertEqual(
            ui_modal.selected_ui_desc,
            DESCRIPTION_TEMPLATE.format("DummyUI", "Dummy UI 2")
        )
