from traits.api import (HasStrictTraits, Instance, List, Button, Either,
                        on_trait_change, Dict, Bool)
from traitsui.api import (View, Handler, HSplit, VGroup, UItem,
                          HGroup, ListStrEditor, InstanceEditor)
from traitsui.list_str_adapter import ListStrAdapter

from force_bdss.api import (
    BaseMCOModel, BaseMCOFactory,
    BaseDataSourceModel, BaseDataSourceFactory,
    BaseMCOParameter, BaseMCOParameterFactory,
    BaseNotificationListenerModel, BaseNotificationListenerFactory,
)

from force_wfmanager.left_side_pane.view_utils import get_factory_name, \
    get_plugin_producer


class ListAdapter(ListStrAdapter):
    """ Adapter for the list of available MCOs/Data sources/KPI calculators
    factories """
    can_edit = Bool(False)

    def get_text(self, object, trait, index):
        if hasattr(self.item, "plugin"):
            return (
                get_plugin_producer(self.item.plugin) +
                " :: " +
                get_factory_name(self.item)
            )
        else:
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
