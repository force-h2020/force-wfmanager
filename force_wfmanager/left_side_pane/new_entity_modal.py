
from __future__ import unicode_literals
from traits.api import (HasStrictTraits, Instance, List, Either,
                        on_trait_change, Dict, Property, Unicode, Bool,
                        ReadOnly)
from traitsui.api import (View, Handler, HSplit, Group, VGroup, UItem,
                          InstanceEditor, OKCancelButtons, Menu,
                          TreeEditor, TreeNode, HTMLEditor)

from envisage.plugin import Plugin

from force_bdss.api import (BaseFactory, BaseMCOModel, BaseDataSourceModel,
                            BaseMCOParameter, BaseNotificationListenerModel)

from force_wfmanager.left_side_pane.view_utils import model_info

no_view = View()
no_menu = Menu()


class ModalHandler(Handler):
    def close(self, info, is_ok):
        if is_ok is False:
            info.object.current_model = None
        return True


class PluginModelView(HasStrictTraits):
    """An instance of PluginModelView contains a plugin, along
    with all the factories which can be derived from it"""
    plugin = Instance(Plugin)
    name = Unicode("plugin")
    factories = List(Instance(BaseFactory))


class Root(HasStrictTraits):
    plugins = List(PluginModelView)
    name = Unicode("root")


class NewEntityModal(HasStrictTraits):
    """ Dialog which allows the user to add a new MCO/Data Source
    to the workflow """
    #: Available factories, this class is generic and can contain any factory
    #: which implement the create_model method
    factories = List(Instance(BaseFactory))

    #: List of PluginModelView instances, which provide a mapping
    # between plugins and factories
    plugins_root = Instance(Root)

    #: Selected factory in the list
    selected_factory = Instance(BaseFactory)

    #: Currently editable model
    current_model = Either(
        Instance(BaseMCOModel),
        Instance(BaseMCOParameter),
        Instance(BaseDataSourceModel),
        Instance(BaseNotificationListenerModel),
    )

    #: Cache for created models, models are created when selecting a new
    #: factory and cached so that when selected_factory change the created
    #: models are saved
    _cached_models = Dict()

    editor = TreeEditor(nodes=[
        TreeNode(node_for=[Root], children="plugins",
                 view=no_view, label="name", menu=no_menu),
        TreeNode(node_for=[PluginModelView], children="factories",
                 view=no_view, label="name", menu=no_menu),
        TreeNode(node_for=[BaseFactory],
                 children="", view=no_view, label="name", menu=no_menu)
            ],
        orientation="vertical",
        selected="selected_factory",
        hide_root=True,
        auto_open=2,
        editable=False
        )

    #: Disable the OK button if no factory set
    OKCancelButtons[0].trait_set(enabled_when="selected_factory is not None")

    model_description_HTML = Property(Unicode, depends_on="current_model")

    current_model_editable = Property(Bool, depends_on="current_model")

    no_config_options_msg = ReadOnly(Unicode)

    traits_view = View(
            HSplit(
                Group(
                    UItem("plugins_root",
                          editor=editor)
                    ),
                VGroup(
                    Group(
                        UItem("current_model",
                              style="custom",
                              editor=InstanceEditor(),
                              visible_when="current_model_editable is True"
                              ),
                        UItem("no_config_options_msg",
                              style="readonly",
                              editor=HTMLEditor(),
                              visible_when="current_model_editable is False"),
                        visible_when="current_model is not None",
                        style="custom",
                        label="Configuration Options",
                        show_border=True,

                    ),
                    Group(
                         UItem("model_description_HTML",
                               editor=HTMLEditor(),
                               ),
                         style="readonly",
                         label="Description",
                         show_border=True
                     ),
                )
                ),
            buttons=OKCancelButtons,
            title="Add New Element",
            handler=ModalHandler(),
            width=800,
            height=600,
            resizable=True,
            kind="livemodal"
            )

    def __init__(self, factories, *args, **kwargs):
        super(NewEntityModal, self).__init__(*args, **kwargs)
        self.factories = factories

    def _plugins_root_default(self):
        """Create a root object for use in the root node of the tree editor.
        This contains a list of PluginModelViews, which hold the plugin itself,
        the plugin's factories and the plugin name"""

        #: A dict with Plugin instances as keys and their associated factories
        #: as values.
        plugin_dict = {}

        for factory in self.factories:
            plugin = self.get_plugin_from_factory(factory)
            if plugin not in plugin_dict:
                plugin_dict[plugin] = []
            plugin_dict[plugin].append(factory)

        # Order the keys alphabetically by plugin name
        ordered_keys = sorted(plugin_dict.keys(), key=lambda p: p.name)

        plugins = []
        for plugin in ordered_keys:
            factories = plugin_dict[plugin]
            plugins.append(PluginModelView(plugin=plugin,
                                           factories=factories,
                                           name=plugin.name))
        return Root(plugins=plugins)

    def _no_config_options_msg_default(self):
        return htmlformat(body="<p>No configuration options "
                          "available for this selection</p>")

    @on_trait_change("selected_factory")
    def update_current_model(self):
        """ Update the current editable model when the selected factory has
        changed. The current model will be created on the fly or extracted from
        the cache if it was already created before """
        if self.selected_factory is None:
            self.current_model = None
            return

        cached_model = self._cached_models.get(self.selected_factory)

        if cached_model is None:
            cached_model = self.selected_factory.create_model()
            self._cached_models[self.selected_factory] = cached_model

        self.current_model = cached_model

    def get_plugin_from_factory(self, factory):
        """Returns the plugin associated with a particular factory"""
        if isinstance(factory, BaseFactory):
            plugin = factory.plugin
            return plugin
        return None

    def _get_current_model_editable(self):
        """A check which indicates if 1. A view with at least
        one item exists for this model and 2. That those items
        are actually visible to the user"""
        return model_info(self.current_model) != []

    def _get_model_description_HTML(self):
        """Format a description of the currently selected model and it's
        parameters, using desc metadata from the traits in
        ${model_name}_model.py"""

        # A default message when no model selected
        if self.selected_factory is None or self.current_model is None:
            return htmlformat("No Model Selected")

        model_name = self.selected_factory.get_name()
        model_desc = self.selected_factory.get_description()
        view_info = model_info(self.current_model)

        # Message for a model without editable traits
        if view_info == []:
            return htmlformat(model_name, model_desc)

        # A list containing trait names and descriptions
        name_desc_pairs = []

        # Retrieve descriptions from trait metadata
        for i, trait_name in enumerate(view_info):
            trait = self.current_model.trait(trait_name)
            trait_desc = trait.desc

            if trait_desc is not None:
                name_desc_pairs.append([trait_name, trait_desc])
            else:
                name_desc_pairs.append([trait_name,
                                        "No description available."])

        # Format names as in the Instance Editor
        name_desc_pairs = [[name.replace("_", " ").capitalize(), desc]
                           for name, desc in name_desc_pairs]

        # Create a HTML string with all the model's parameters
        return htmlformat(model_name, model_desc, name_desc_pairs)


# A generic HTML header and body with title and text
def htmlformat(factory_title=None, factory_description=None,
               parameter_info=None, body=None):
    html = """
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
            {body}
        </body>
        </html>
        """

    titled_paragraph = """
        <div class="container">
            <h2>{name}</h2>
            <p>{description}</p>
        </div>
        """
    if body is not None:
        return html.format(body=body)

    if factory_title is not None:
        body = ["<h1>{factory_title}</h1>".format(factory_title=factory_title)]
    else:
        body = []

    if factory_description is not None:
        body.append("<p>{description}</p>".format(
            description=factory_description)
        )
    if parameter_info is not None:
        for name, description in parameter_info:
            parameter_html = titled_paragraph.format(
                name=name, description=description
            )
            body.append(parameter_html)

    return html.format(body="".join(body))
