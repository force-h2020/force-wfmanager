from traitsui.editors import HTMLEditor
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

    selected_plugin_message = Str()

    def __init__(self, plugins):
        super(PluginDialog, self).__init__(plugins=plugins)

    def default_traits_view(self):
        return View(
            HGroup(
                HGroup(
                    UItem('plugins', editor=ListStrEditor(
                        selected="selected_plugin",
                        editable=False,
                        adapter=PluginAdapter()
                    )),
                    UItem('selected_plugin_message',
                          style="readonly",
                          editor=HTMLEditor()),
                ),
                label="Plugins",
                show_border=True
            )
        )

    @on_trait_change('selected_plugin')
    def _sync_error(self):
        plugin = self.selected_plugin
        if plugin is None:
            self.selected_plugin_message = htmlformat(
                "Please select a plugin",
                "")
            return

        if plugin.broken:
            self.selected_plugin_message = htmlformat("Plugin Error",
                                                      plugin.error_msg)
            return

        self.selected_plugin_message = htmlformat("", "No errors for this plugin.")


def htmlformat(title, message):
    return """
        <html>
        <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
            <style type="text/css">
                .container{{
                    width: 100%;
                    display: block;
                }}
            </style>
        </head>
        <body>
        <h1>{}</h1>
        <p>{}</p>
        </body>
        </html>
        """.format(title, message)

