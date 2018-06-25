from traits.api import (HasStrictTraits, Instance, List, Button,
                        Either, on_trait_change, Dict, Str)
from traitsui.api import (View, Handler, HSplit, VGroup, UItem,
                          InstanceEditor, OKCancelButtons,
                          TreeEditor, TreeNode)

from envisage.plugin import Plugin


from force_bdss.api import (
    BaseMCOModel, BaseMCOFactory,
    BaseDataSourceModel, BaseDataSourceFactory,
    BaseMCOParameter, BaseMCOParameterFactory,
    BaseNotificationListenerModel, BaseNotificationListenerFactory)

no_view = View()


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

    add_button = Button("Add")
    cancel_button = Button('Cancel')

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
                 view=no_view, label='name'),
        TreeNode(node_for=[PluginModelView], children='factories',
                 view=no_view, label='name'),
        TreeNode(node_for=[BaseMCOFactory, BaseNotificationListenerFactory,
                           BaseDataSourceFactory, BaseMCOParameterFactory],
                 children='', view=no_view, label='name')
            ],
        orientation="vertical",
        selected="selected_factory",
        hide_root=True,
        auto_open=2,
        editable=False
        )

    #: Disable the OK button if no factory set
    OKCancelButtons[0].trait_set(enabled_when="selected_factory is not None")

    traits_view = View(
        VGroup(
            HSplit(
                UItem('plugins_root', editor=editor),

                UItem('current_model', style='custom', editor=InstanceEditor())
                ),
        ),
        buttons=OKCancelButtons,
        title='Add New Element',
        handler=ModalHandler(),
        width=800,
        height=600,
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
