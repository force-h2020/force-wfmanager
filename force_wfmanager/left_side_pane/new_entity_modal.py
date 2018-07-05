from traits.api import (HasStrictTraits, Instance, List, Either,
                        on_trait_change, Dict, Str, Property, HTML, Bool)
from traitsui.api import (View, Handler, HSplit, Group, VGroup, UItem, Item,
                          InstanceEditor, OKCancelButtons, Menu,
                          TreeEditor, TreeNode, HTMLEditor, TextEditor)

from envisage.plugin import Plugin

from force_bdss.api import (
    BaseMCOModel, BaseMCOFactory,
    BaseDataSourceModel, BaseDataSourceFactory,
    BaseMCOParameter, BaseMCOParameterFactory,
    BaseNotificationListenerModel, BaseNotificationListenerFactory)

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
    name = Str('plugin')
    factories = List(Either(Instance(BaseMCOFactory),
                            Instance(BaseMCOParameterFactory),
                            Instance(BaseDataSourceFactory),
                            Instance(BaseNotificationListenerFactory)))


class Root(HasStrictTraits):
    plugins = List(PluginModelView)
    name = Str("root")


class NewEntityModal(HasStrictTraits):
    """ Dialog which allows the user to add a new MCO/Data Source
    to the workflow """
    #: Available factories, this class is generic and can contain any factory
    #: which implement the create_model method
    factories = Either(
        List(Instance(BaseMCOFactory)),
        List(Instance(BaseMCOParameterFactory)),
        List(Instance(BaseDataSourceFactory)),
        List(Instance(BaseNotificationListenerFactory)),
    )

    #: List of PluginModelView instances, which provide a mapping
    # between plugins and factories
    plugins_root = Instance(Root)

    #: Selected factory in the list
    selected_factory = Either(
        Instance(BaseMCOFactory),
        Instance(BaseMCOParameterFactory),
        Instance(BaseDataSourceFactory),
        Instance(BaseNotificationListenerFactory),
    )

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
        TreeNode(node_for=[Root], children='plugins',
                 view=no_view, label='name', menu=no_menu),
        TreeNode(node_for=[PluginModelView], children='factories',
                 view=no_view, label='name', menu=no_menu),
        TreeNode(node_for=[BaseMCOFactory, BaseNotificationListenerFactory,
                           BaseDataSourceFactory, BaseMCOParameterFactory],
                 children='', view=no_view, label='name', menu=no_menu)
            ],
        orientation="vertical",
        selected="selected_factory",
        hide_root=True,
        auto_open=2,
        editable=False
        )

    #: Disable the OK button if no factory set
    OKCancelButtons[0].trait_set(enabled_when="selected_factory is not None")

    model_description_HTML = Property(HTML, depends_on="current_model")

    current_model_editable = Property(Bool, depends_on='current_model')

    default_text = Str('No Configuration Options')

    traits_view = View(
            HSplit(
                Group(
                    UItem('plugins_root',
                          editor=editor)
                    ),
                VGroup(
                    Group(
                        UItem('current_model',
                              style='custom',
                              editor=InstanceEditor(),
                              visible_when='current_model_editable is True'
                              ),
                        UItem('default_text',
                              style='readonly',
                              editor=TextEditor(),
                              visible_when='current_model_editable is False'),
                        visible_when='current_model is not None',
                        style="custom",
                        label="Configuration Options",
                        show_border=True,

                    ),
                    Group(
                         UItem('model_description_HTML',
                               editor=HTMLEditor(),
                               ),
                         style="readonly",
                         label="Description",
                         show_border=True
                     ),
                )
                ),
            buttons=OKCancelButtons,
            title='Add New Element',
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
        # Build up a list of plugin-factory mappings
        plugin_dict = {}
        for factory in self.factories:
            plugin_from_factory = self.get_plugin_from_factory(factory)
            if plugin_from_factory not in plugin_dict:
                plugin_dict[plugin_from_factory] = []
            plugin_dict[plugin_from_factory].append(factory)

        plugins = []
        for plugin, factories in zip(plugin_dict, plugin_dict.values()):
            plugins.append(PluginModelView(plugin=plugin,
                                           factories=factories,
                                           name=plugin.id))
        return Root(plugins=plugins)

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
        if isinstance(factory, (BaseMCOFactory, BaseDataSourceFactory,
                                BaseNotificationListenerFactory)):
            plugin = factory.plugin
        # The MCO parameter factory does not contain it's own plugin, but does
        # contain the mco_factory it is associated with
        else:
            plugin = factory.mco_factory.plugin

        return plugin

    def _get_current_model_editable(self):
        """A check which indicates if 1. A view with at least
        one item exists for this model and 2. That those items
        are actually visible to the user"""
        if self.current_model is None:
            return False

        view_info = self.view_structure()

        view_info = [trait_name for trait_name in
                     view_info if trait_name in
                     self.current_model.visible_traits()]

        if view_info == []:
            return False

        return True

    def _get_model_description_HTML(self):
        """Format a description of the currently selected model and it's
        parameters, using desc metadata from the traits in
        ${model_name}_model.py"""

        # A default message when no model selected
        if self.selected_factory is None or self.current_model is None:
            return html_string.format("No Model Selected", "")

        model_name = self.selected_factory.get_name()
        view_info = self.view_structure()

        # Message for a model without editable traits
        if view_info == []:
            return html_string.format(model_name, "")

        # Remove traits in the view which are not editable
        view_info = [trait_name for trait_name in
                     view_info if trait_name in
                     self.current_model.visible_traits()]

        # Retrieve descriptions from trait metadata
        for i, trait_name in enumerate(view_info):
            trait = self.current_model.trait(trait_name)
            trait_desc = trait.desc

            if trait_desc is not None:
                view_info[i] = [trait_name, trait_desc]
            else:
                view_info[i] = [trait_name, 'No Description Available']

        # Format names as in the Instance Editor
        view_info = [[name.replace('_', ' ').capitalize(), desc]
                     for name, desc in view_info]

        # Create a HTML string with all the model's parameters
        body_str = ''.join([title_para.format(name, desc)
                           for name, desc in view_info])

        return html_string.format(model_name, body_str)

    def view_structure(self):
        """Return a list of editable traits in the order
        they appear in the view for the current model"""
        #: The View of current_model
        current_model_view = self.current_model.trait_view()
        #: A List containing the Groups/Items in this View
        main_group_contents = current_model_view.content.content
        #: A List of items from our view in the order they appear in the view.
        #: This function does not do anything clever for unusual view layouts
        main_group_items = _item_info_from_group(main_group_contents)
        return main_group_items


def _item_info_from_group(group_contents, item_info=None):
    """Gets the item names from a list of groups (group_contents).
    Returns a list of trait names corresponding to the items in the group.
    """
    if item_info is None:
        item_info = []

    for object in group_contents:
        # For a Group, call this function again - which sets the items found
        # in any subgroups as item_info
        if isinstance(object, Group):
            item_info = _item_info_from_group(object.content, item_info)
        # For an Item, add the item's name to item_info
        elif isinstance(object, Item):
            item_info.append(object.name)
    return item_info


# A generic HTML header
html_string = """
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
        {}
        </body>
        </html>
        """

# HTML for a title and description
title_para = """
        <div class="container">
            <h2>{}</h2>
            <p>{}</p>
        </div>
        """
