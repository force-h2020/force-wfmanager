from traits.api import (HasStrictTraits, Instance, List, Button, Either,
                        on_trait_change, Dict, Bool, Str)
from traitsui.api import (View, Handler, HSplit, VGroup, UItem,
                          HGroup, ListStrEditor, InstanceEditor)
from traitsui.list_str_adapter import ListStrAdapter

from force_bdss.api import (
    BaseMCOModel, BaseMCOFactory,
    BaseDataSourceModel, BaseDataSourceFactory,
    BaseMCOParameter, BaseMCOParameterFactory,
    BaseNotificationListenerModel, BaseNotificationListenerFactory,
)

from force_wfmanager.left_side_pane.view_utils import get_factory_name


class ListAdapter(ListStrAdapter):
    """ Adapter for the list of available MCOs/Data sources/KPI calculators
    factories """
    can_edit = Bool(False)

    def get_text(self, object, trait, index):
        return get_factory_name(self.item)


class ModalHandler(Handler):
    def object_add_button_changed(self, info):
        """ Action triggered when clicking on "Add" button in the modal """
        info.ui.dispose()

    def object_cancel_button_changed(self, info):
        """ Action triggered when clicking on "Cancel" button in the modal """
        info.object.current_model = None
        info.ui.dispose()


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

    traits_view = View(
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
    )

    def __init__(self, factories, *args, **kwargs):
        super(NewEntityModal, self).__init__(*args, **kwargs)
        self.factories = factories
        # self.factories = sorted(self.factories, key=self.get_plugin_info)
        self.factory_group_by_creator()
        self.trait_view(name='traits_view',
                        view_element=self.factory_group_view())

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

    def factory_group_by_creator(self):
        """Takes the list of factories and creates a dict with keys=
        creator_name and values=factories. This also adds a trait named
        ${creator_name}_factories for each creator name"""
        factory_dict = {}
        for factory in self.factories:
            plugin_creator = self.get_plugin_info(factory)
            if plugin_creator in factory_dict:
                factory_dict[plugin_creator].append(factory)
            else:
                factory_dict[plugin_creator] = [factory]
                
        #for key in self.factory_dict:
        #    self.add_trait(str(key)+'_factories', List(factory_dict[key]))

    def factory_group_view(self):
        uitem_list = []
        for key in self.factory_dict:
            title_str = key
            uitem_list.append(UItem(
                "{}_factories".format(key),
                editor=ListStrEditor(
                    adapter=ListAdapter(),
                    selected="selected_factory",
                    title=title_str
                ),
            ))
        view = View(
            VGroup(
                HSplit(
                    HGroup(uitem_list),
                    UItem('current_model', style='custom',
                          editor=InstanceEditor())
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
        )
        return view

    def get_plugin_info(self, factory):
        """Returns the module name of the plugin this factory is associated
        with"""
        plugin_class = ''
        if isinstance(factory, (BaseMCOFactory, BaseDataSourceFactory,
                                BaseNotificationListenerFactory)):
            plugin_class = str(factory.plugin.__class__)
        elif isinstance(factory, BaseMCOParameterFactory):
            plugin_class = str(factory.mco_factory.plugin.__class__)
        plugin_creator = plugin_class.split("\'")[1].split('.')[0]

        # if isinstance(factory, (BaseMCOFactory, BaseDataSourceFactory,
        #                        BaseNotificationListenerFactory)):
        #     plugin_id = factory.plugin.id.split('.')
        # elif isinstance(factory, BaseMCOParameterFactory):
        #     plugin_id = factory.mco_factory.plugin.id.split('.')
        # plugin_creator = [plugin_id[2], plugin_id[4], plugin_id[5]]

        return plugin_creator
