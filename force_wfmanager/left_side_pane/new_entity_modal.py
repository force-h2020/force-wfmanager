from traits.api import (HasStrictTraits, Instance, List, Button,
                        Either, on_trait_change, Dict, Str)
from traitsui.api import (View, Handler, HSplit, VGroup, UItem,
                          HGroup, InstanceEditor,
                          TreeEditor, TreeNode)

from envisage.plugin import Plugin


from force_bdss.api import (
    BaseMCOModel, BaseMCOFactory,
    BaseDataSourceModel, BaseDataSourceFactory,
    BaseMCOParameter, BaseMCOParameterFactory,
    BaseNotificationListenerModel, BaseNotificationListenerFactory,
)


class ModalHandler(Handler):
    def object_add_button_changed(self, info):
        """ Action triggered when clicking on "Add" button in the modal """
        info.ui.dispose()

    def object_cancel_button_changed(self, info):
        """ Action triggered when clicking on "Cancel" button in the modal """
        info.object.current_model = None
        info.ui.dispose()


class FactoryPlugin(HasStrictTraits):
    """An instance of FactoryPlugin contains a plugin, along with all the factories
    which can be derived from it"""
    plugin = Instance(Plugin)
    name = Str('plugin')
    plugin_factories = List(Either(Instance(BaseMCOFactory),
                                   Instance(BaseMCOParameterFactory),
                                   Instance(BaseDataSourceFactory),
                                   Instance(BaseNotificationListenerFactory)))


class Root(HasStrictTraits):
    plugins = List(FactoryPlugin)
    name = Str("root")


class NewEntityModal(HasStrictTraits):
    """ Dialog which allows the user to add a new MCO/Data Source
    to the workflow """
    #: Available factories, this class is generic and can contain any factory
    #: which implement the create_model method
    factory_list = Either(
        List(Instance(BaseMCOFactory)),
        List(Instance(BaseMCOParameterFactory)),
        List(Instance(BaseDataSourceFactory)),
        List(Instance(BaseNotificationListenerFactory)),
    )

    #: List of FactoryPlugin instances, which provide a mapping between plugins
    #: factories
    plugins = Instance(Root)

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

    """traits_view = View(
        VGroup(
            HSplit(
                UItem(
                    "factories",
                    editor=ListStrEditor(
                        adapter=ListAdapter(),
                        selected="selected_factory"),
                ),
                UItem('current_model', style='custom', editor=InstanceEditor())
            ),
            HGroup(
                UItem(
                    'add_button',
                    enabled_when="selected_factory is not None"
                ),
                UItem('cancel_button')
            )
        ),
        title='New Element',
        handler=ModalHandler(),
        width=800,
        height=600,
        kind="livemodal"
    )"""

    editor = TreeEditor(nodes=[
        TreeNode(node_for=[Root], children='plugins',
                 view=View(), label='name'),
        TreeNode(node_for=[FactoryPlugin], children='plugin_factories',
                 view=View(), label='name'),
        TreeNode(node_for=[BaseMCOFactory, BaseNotificationListenerFactory,
                           BaseDataSourceFactory, BaseMCOParameterFactory],
                 children='', view=View(), label='name')
            ],
        orientation="vertical",
        selected="selected_factory",
        hide_root=True,
        )

    traits_view = View(
        VGroup(
            HSplit(
                UItem('plugins', editor=editor),
                UItem('current_model', style='custom', editor=InstanceEditor())
                ),
            HGroup(
                UItem('add_button',
                      enabled_when="selected_factory is not None"),
                UItem('cancel_button')
            )
        ),
        title='New Element',
        handler=ModalHandler(),
        width=800,
        height=600,
        kind="livemodal"
    )

    def __init__(self, factories, *args, **kwargs):
        super(NewEntityModal, self).__init__(*args, **kwargs)
        self.factory_list = factories

        # Build up a list of plugin-factory mappings
        plugin_dict = {}
        for factory in self.factory_list:
            plugin_from_factory = self._get_plugin(factory)
            if plugin_from_factory not in plugin_dict:
                plugin_dict[plugin_from_factory] = []
            plugin_dict[plugin_from_factory].append(factory)

        plugins = []
        for plugin, factory_list in zip(plugin_dict, plugin_dict.values()):
            plugins.append(FactoryPlugin(plugin=plugin,
                                         plugin_factories=factory_list,
                                         name=plugin.id))
        self.plugins = Root(plugins=plugins)

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

    def _get_plugin(self, factory):
        if isinstance(factory, (BaseMCOFactory, BaseDataSourceFactory,
                                BaseNotificationListenerFactory)):
            plugin = factory.plugin
        # MCO parameter factory does not contain it's own plugin, but does
        # contain the mco_factory it is associated with
        else:
            plugin = factory.mco_factory.plugin

        return plugin
