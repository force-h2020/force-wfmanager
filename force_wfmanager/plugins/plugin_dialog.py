from traitsui.editors import HTMLEditor
from traitsui.list_str_adapter import ListStrAdapter
from traitsui.api import View, UItem, ListStrEditor, HGroup

from traits.api import (
    HasStrictTraits, List, Instance, Unicode,
    on_trait_change
)

from force_bdss.api import BaseExtensionPlugin


class PluginAdapter(ListStrAdapter):
    def _get_text(self):
        return self.item.name if self.item.name else self.item.id

    def _get_text_color(self):
        if self.item.broken:
            return "#FF0000"
        return super(PluginAdapter, self)._get_text_color()


class PluginDialog(HasStrictTraits):
    """Displays a list of the available plugins, together with their
    description.
    """
    # -------------------
    # Required Attributes
    # -------------------

    #: A list of all available plugins
    plugins = List(Instance(BaseExtensionPlugin))

    # ------------------
    # Regular Attributes
    # ------------------

    #: The currently selected plugin
    selected_plugin = Instance(BaseExtensionPlugin)

    # --------------------
    # Dependent Attributes
    # --------------------

    #: An HTML description of the selected plugin
    #: Listens to :attr:`selected_plugin`
    selected_plugin_HTML = Unicode()

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
                    UItem('selected_plugin_HTML',
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
            self.selected_plugin_HTML = htmlformat(
                title="No plugin selected")
            return

        if plugin.broken:
            self.selected_plugin_HTML = htmlformat(
                title=plugin.id,
                error_msg=plugin.error_msg,
                error_tb=plugin.error_tb
            )
            return

        self.selected_plugin_HTML = htmlformat(
            title=plugin.name,
            version=plugin.version,
            description=plugin.description
        )

    def _selected_plugin_HTML_default(self):
        return htmlformat("No plugin selected")


def htmlformat(title, version=None, description=None, error_msg=None,
               error_tb=None):
    """Formats information about the plugin as HTML, which is displayed within
    the PluginDialog window.
    Parameters
    ----------
    title: Unicode
        The name or id of the plugin.
    version: Unicode


    """
    html = """
        <html>
        <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
            <style type="text/css">
                body{{
                    font-family: sans-serif;
                }}
                .container{{
                    width: 100%;
                    font-family: sans-serif;
                    display: block;
                }}
            </style>
        </head>
        <body>
        {body}
        </body>
        </html>
        """

    body = [
        "<h1>{title}</h1>".format(title=title)
    ]

    if version is not None:
        body.append("<p>Version: {version}</p>".format(version=version))

    if description:
        body.append("<p>{description}</p>".format(description=description))

    if error_msg:
        body.append("<h4>Error: {error_msg}</h4>".format(error_msg=error_msg))

        if error_tb:
            body.append("<h4>Traceback</h4>")
            body.append("<pre>{error_tb}</pre>".format(error_tb=error_tb))

    return html.format(body="".join(body))
