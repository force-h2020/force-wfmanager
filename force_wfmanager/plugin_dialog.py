from traitsui.list_str_adapter import ListStrAdapter

from force_bdss.api import BaseExtensionPlugin
from traits.api import (
    HasStrictTraits, List, Instance, Str,
    on_trait_change
)
from traitsui.api import View, UItem, ListStrEditor, HGroup


class PluginAdapter(ListStrAdapter):
    def _get_text(self):
        return self.item.id

    def _get_image(self):
        return 'icons/invalid.png' if self.item.broken else 'icons/valid.png'


class PluginDialog(HasStrictTraits):
    plugins = List(Instance(BaseExtensionPlugin))

    selected_plugin = Instance(BaseExtensionPlugin)

    selected_plugin_error = Str()

    def __init__(self, plugins):
        super(PluginDialog, self).__init__(plugins=plugins)

    def default_traits_view(self):
        return View(
            HGroup(
                UItem('plugins', editor=ListStrEditor(
                    selected="selected_plugin",
                    editable=False,
                    adapter=PluginAdapter()
                )),
                UItem('selected_plugin_error', style="readonly"),
                label="Plugins",
                show_border=True
            )
        )

    @on_trait_change('selected_plugin')
    def _sync_error(self):
        print("XXX")
        if self.selected_plugin is not None:
            self.selected_plugin_error = self.selected_plugin.error_msg
            return

        self.selected_plugin_error = "No errors for this plugin."
