from traits.api import (HasStrictTraits, Instance, List, Button, Either,
                        on_trait_change, Dict)
from traitsui.api import (View, Handler, HSplit, VGroup, UItem,
                          HGroup, ListStrEditor, InstanceEditor)
from traitsui.list_str_adapter import ListStrAdapter

from force_bdss.api import (
    BaseMCOModel, BaseMCOBundle,
    BaseDataSourceModel, BaseDataSourceBundle,
    BaseKPICalculatorModel, BaseKPICalculatorBundle,
    BaseMCOParameter, BaseMCOParameterFactory)

from .workflow_model_view import WorkflowModelView
from .view_utils import get_bundle_name


class ListAdapter(ListStrAdapter):
    """ Adapter for the list of available MCOs/Data sources/KPI calculators
    bundles """
    def get_text(self, object, trait, index):
        return get_bundle_name(self.item)


class ModalHandler(Handler):
    def object_add_button_changed(self, info):
        """ Action triggered when clicking on "Add" button in the modal """
        if info.object.current_model is not None:
            info.object.workflow_mv.add_entity(info.object.current_model)
        info.ui.dispose(True)

    def object_cancel_button_changed(self, info):
        """ Action triggered when clicking on "Cancel" button in the modal """
        info.ui.dispose(False)


class NewEntityModal(HasStrictTraits):
    """ Dialog which allows the user to add a new MCO/Data Source/KPI
    calculator to the workflow """
    workflow_mv = Instance(WorkflowModelView)

    #: Available factories, this class is generic and can contain any factory
    #: which implement the create_model method
    available_factories = Either(
        List(Instance(BaseMCOBundle)),
        List(Instance(BaseMCOParameterFactory)),
        List(Instance(BaseDataSourceBundle)),
        List(Instance(BaseKPICalculatorBundle)),
    )

    #: Selected factory in the list
    selected_factory = Either(
        Instance(BaseMCOBundle),
        Instance(BaseMCOParameterFactory),
        Instance(BaseDataSourceBundle),
        Instance(BaseKPICalculatorBundle)
    )

    add_button = Button("Add")
    cancel_button = Button('Cancel')

    #: Currently editable model
    current_model = Either(
        Instance(BaseMCOModel),
        Instance(BaseMCOParameter),
        Instance(BaseDataSourceModel),
        Instance(BaseKPICalculatorModel)
    )

    #: Cache for created models, models are created when selecting a new
    #: factory and cached so that when selected_factory change the created
    #: models are saved
    _cached_models = Dict()

    traits_view = View(
        VGroup(
            HSplit(
                UItem(
                    "available_factories",
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
