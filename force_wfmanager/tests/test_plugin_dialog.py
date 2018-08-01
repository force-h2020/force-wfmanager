import unittest
import testfixtures

from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from traits.api import HasTraits, Instance

from force_bdss.base_extension_plugin import BaseExtensionPlugin
from force_wfmanager.plugin_dialog import htmlformat, PluginDialog


class UIDummy:
    def dispose(self):
        pass


class ModalInfoDummy(HasTraits):
    object = Instance(PluginDialog)

    ui = Instance(UIDummy)

    def _ui_default(self):
        return UIDummy()


class Plugin1(BaseExtensionPlugin):
    def get_name(self):
        return "Plugin1"

    def get_description(self):
        return "Plugin1 description"

    def get_version(self):
        return 0

    def get_factory_classes(self):
        return []


class Plugin2(BaseExtensionPlugin):
    def get_name(self):
        return "Plugin2"

    def get_description(self):
        return "Plugin2 description"

    def get_version(self):
        return 1

    def get_factory_classes(self):
        raise Exception("Boom")


class TestPluginDialog(GuiTestAssistant, unittest.TestCase):

    def test_htmlformat(self):
        self.assertIn("<h1>xxx</h1>", htmlformat("xxx"))
        self.assertIn("foo", htmlformat(
            title="foo", error_msg="frop", error_tb="woo"))

    def _get_dialog(self):
        with testfixtures.LogCapture():
            modal = PluginDialog(plugins=[Plugin1(), Plugin2()])
        return modal, ModalInfoDummy(object=modal)

    def test_dialog(self):
        modal, modal_info = self._get_dialog()
        self.assertEqual(modal.selected_plugin, None)
        self.assertIn("No plugin selected", modal.selected_plugin_HTML)

        modal.selected_plugin = modal.plugins[0]

        self.assertIn("Plugin1 description", modal.selected_plugin_HTML)

        modal.selected_plugin = modal.plugins[1]

        self.assertIn("Boom", modal.selected_plugin_HTML)

        modal.selected_plugin = None

        self.assertIn("No plugin selected", modal.selected_plugin_HTML)

    def test_show(self):
        modal, modal_info = self._get_dialog()

        with self.event_loop():
            ui = modal.edit_traits()

        with self.delete_widget(ui.control):
            ui.dispose()
