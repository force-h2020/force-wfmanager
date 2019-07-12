from traits.api import (
    Bool, Callable, Dict, Either, HasStrictTraits, Instance, List, ReadOnly,
    Property, Unicode, on_trait_change
)
from traitsui.api import (
    HSplit, HTMLEditor, InstanceEditor, Menu, TreeEditor, TreeNode, UItem,
    VGroup, View
)
from envisage.plugin import Plugin

from force_bdss.api import BaseFactory, BaseMCOParameter, BaseModel
from force_wfmanager.ui.ui_utils import model_info

no_view = View()
no_menu = Menu()


class PluginModelView(HasStrictTraits):
    """The ModelView for each separate plugin. The ModelViews are displayed
    in the TreeEditor of the NewEntityCreator.
    """
    #: An instance of an external Envisage Plugin.
    plugin = Instance(Plugin)

    #: The name of the PluginModelView
    name = Unicode("plugin")

    #: A list of all the factories which are derived from :attr:`plugin`.
    #: The factories will all be of type BaseFactory
    factories = List(Instance(BaseFactory))


class Root(HasStrictTraits):
    """A Root node, required by the TreeEditor.
    """
    #: A list of all the PluginModelViews.
    plugins = List(PluginModelView)

    #: A name for the Root node
    name = Unicode("root")


class NewEntityCreator(HasStrictTraits):
    """A Traits class which is viewed in the UI as a tree editor containing
    the DataSource/MCO/Parameter/NotificationListener factories for the
    currently installed plugins.
     """

    # -------------------
    # Required Attributes
    # -------------------

    #: A list of available factories for this NewEntityCreator.
    #: This list uses the generic BaseFactory class and
    #: so can contain a mixture of factory types.
    factories = List(Instance(BaseFactory))

    #: A function which is called on double clicking an item in the workflow
    #: tree. Currently this is used to allow adding a new item to the workflow
    #: by double clicking it in the UI.
    dclick_function = Callable()

    # ------------------
    # Regular Attributes
    # ------------------

    #: The root node displayed in the TreeEditor
    plugins_root = Instance(Root)

    #: A message to be displayed if there are no config options
    _no_config_options_msg = ReadOnly(Unicode)

    #: Option for the user to manually control the visibility of the
    #: configuration option display
    config_visible = Bool(True)

    # Factory name to be displayed in view_header
    factory_name = Unicode()

    # --------------------
    # Dependent Attributes
    # --------------------

    #: The currently selected factory in the TreeEditor
    #: Listens to: TreeEditor (see :func:`default_traits_view`)
    selected_factory = Instance(BaseFactory)

    #: An instance of the model created by the currently selected factory.
    #: On a change of :attr:`selected_factory`, the factory's create_model
    #: method is called and the returned object set as model.
    #: Listens to :attr:`selected_factory`
    model = Either(Instance(BaseModel), Instance(BaseMCOParameter))

    #: Cache for created models, models are created when selecting a new
    #: factory and cached so that when selected_factory changes the created
    #: models are saved
    #: Listens to :attr:`selected_factory`
    _cached_models = Dict()

    # ----------
    # Properties
    # ----------

    #: HTML header containing the factory name
    view_header = Property(Instance(Unicode), depends_on='factory_name')

    #: HTML containing a model description, obtained from the model's
    #: get_name and get_description methods.
    model_description_HTML = Property(Unicode, depends_on="model")

    #: A Bool which is True if model has a view with at least one user
    #: editable attribute, False otherwise.
    _current_model_editable = Property(Bool, depends_on="model")

    def __init__(self, factories, *args, **kwargs):
        super(NewEntityCreator, self).__init__(*args, **kwargs)
        self.factories = factories

    def default_traits_view(self):
        """ Sets up a view containing a TreeEditor for the currently loaded
        plugins, a sub-view for the selected model and a description of the
        selected model."""
        editor = TreeEditor(nodes=[
            TreeNode(
                node_for=[Root], children="plugins", view=no_view,
                label="name", menu=no_menu
            ),
            TreeNode(
                node_for=[PluginModelView], children="factories",
                view=no_view, label="name", menu=no_menu
            ),
            TreeNode(
                node_for=[BaseFactory], children="", view=no_view,
                label="name", menu=no_menu, on_dclick=self.dclick_function
            )
        ],
            orientation="vertical",
            selected="selected_factory",
            hide_root=True,
            auto_open=2,
            editable=False
        )

        view = View(
                HSplit(
                    VGroup(
                        UItem("view_header",
                              editor=InstanceEditor(),
                              style='custom'
                              ),
                        UItem("plugins_root",
                              editor=editor
                              ),
                        springy=True
                    ),
                    VGroup(
                        VGroup(
                            UItem(
                                "model",
                                style="custom",
                                editor=InstanceEditor(),
                                visible_when="_current_model_editable"
                                  ),
                            UItem(
                                "_no_config_options_msg", style="readonly",
                                editor=HTMLEditor(),
                                visible_when="not _current_model_editable"
                            ),
                            visible_when="model is not None "
                                         "and config_visible",
                            style="custom",
                            label="Configuration Options",
                            show_border=True,
                            springy=True,
                        ),
                        VGroup(
                            UItem("model_description_HTML",
                                  editor=HTMLEditor()),
                            style="readonly",
                            label="Description",
                            show_border=True,
                            springy=True,
                        ),
                    ),
                    springy=True,
                ),
                title="Add New Element",
                width=500,
                resizable=True,
                kind="livemodal"
        )

        return view

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
            plugins.append(PluginModelView(
                plugin=plugin, factories=factories, name=plugin.name
            ))
        return Root(plugins=plugins)

    def __no_config_options_msg_default(self):
        """A message to be displayed for models with no configuration options
        """
        return htmlformat(body="<p>No configuration options "
                          "available for this selection</p>")

    def _get_view_header(self):
        if self.factory_name == '':
            return "<h1>Available Factories</h1>"
        return f"<h1>Available {self.factory_name} Factories</h1>"

    @on_trait_change("selected_factory")
    def update_current_model(self):
        """ Update the current editable model when the selected factory has
        changed. The current model will be created on the fly or extracted from
        the cache if it was already created before """
        if self.selected_factory is None:
            self.model = None
            return

        cached_model = self._cached_models.get(self.selected_factory)

        if cached_model is None:
            cached_model = self.selected_factory.create_model()
            self._cached_models[self.selected_factory] = cached_model

        self.model = cached_model

    def reset_model(self):
        """Helper function which 'resets' self.model to be a new un-edited
        model for the currently selected factory"""
        if self.selected_factory is None:
            self.model = None
        else:
            self.model = self.selected_factory.create_model()

    def get_plugin_from_factory(self, factory):
        """Returns the plugin associated with a particular factory

        Parameters
        ----------
        factory: BaseFactory
            The factory to get plugin information for.
        """
        plugin = factory.plugin
        return plugin

    def _get__current_model_editable(self):
        """A check which returns True if 1. A view with at least
        one item exists for this model and 2. Those items
        are actually visible to the user."""
        return model_info(self.model) != []

    def _get_model_description_HTML(self):
        """Return a HTML formatted description of the currently selected
        model and its parameters. This is constructed from the currently
        selected factory's get_name and get_description methods, alongside the
        the :attr:`desc` attribute of the current model's attributes.
        """

        # A default message when no model selected
        if self.selected_factory is None or self.model is None:
            return htmlformat("No Model Selected")

        model_name = self.selected_factory.get_name()
        model_desc = self.selected_factory.get_description()
        view_info = model_info(self.model)

        # Message for a model without editable traits
        if not view_info:
            return htmlformat(model_name, model_desc)

        # A list containing trait names and descriptions
        name_desc_pairs = []

        # Retrieve descriptions from trait metadata
        for model_attr_name in view_info:
            model_attr = self.model.trait(model_attr_name)
            model_attr_desc = model_attr.desc
            model_attr_label = model_attr.label

            if model_attr_label is not None:
                name = model_attr_label
            else:
                name = model_attr_name.replace("_", " ").capitalize()

            if model_attr_desc is not None:
                name_desc_pairs.append([name, model_attr_desc])
            else:
                name_desc_pairs.append([
                    name, "No description available."
                ])

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
                body{{
                    font-family: sans-serif;
                }}
                .container{{
                    font-family: sans-serif;
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
