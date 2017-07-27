from traits.api import (HasStrictTraits, Instance, List, Button, Either,
                        on_trait_change, Dict)
from traitsui.api import (View, Handler, HSplit, VGroup, UItem,
                          HGroup, ListStrEditor, InstanceEditor)
from traitsui.list_str_adapter import ListStrAdapter

from force_bdss.api import (BaseMCOModel, BaseMultiCriteriaOptimizerBundle,
                            BaseDataSourceModel, BaseDataSourceBundle,
                            BaseKPICalculatorModel, BaseKPICalculatorBundle)

from .workflow_model_view import WorkflowModelView
from .view_utils import get_bundle_name


class ListAdapter(ListStrAdapter):
    """ Adapter for the list of available MCOs/Data sources/KPI calculators
    bundles """
    def get_text(self, object, trait, index):
        return get_bundle_name(self.item)


class ModalHandler(Handler):
    def object_add_button_changed(self, info):
        if info.object.current_model is not None:
            info.object.workflow.add_entity(info.object.current_model)
        info.ui.dispose(True)

    def object_cancel_button_changed(self, info):
        info.ui.dispose(False)


class NewEntityModal(HasStrictTraits):
    """ Dialog which allows the user to add a new MCO/Data Source/KPI
    calculator to the workflow """
    workflow = Instance(WorkflowModelView)

    #: Available bundles, this class is generic and can contain any bundle
    #: which implement the create_model method
    available_bundles = Either(
        List(Instance(BaseMultiCriteriaOptimizerBundle)),
        List(Instance(BaseDataSourceBundle)),
        List(Instance(BaseKPICalculatorBundle)),
    )

    #: Selected bundle in the list
    selected_bundle = Either(
        Instance(BaseMultiCriteriaOptimizerBundle),
        Instance(BaseDataSourceBundle),
        Instance(BaseKPICalculatorBundle)
    )

    add_button = Button("Add")
    cancel_button = Button('Cancel')

    #: Currently editable model
    current_model = Either(
        Instance(BaseMCOModel),
        Instance(BaseDataSourceModel),
        Instance(BaseKPICalculatorModel)
    )

    #: Cache for created models, models are created when selecting a new bundle
    #: and cached so that when selected_bundle change the created models are
    #: saved
    _models = Dict()

    traits_view = View(
        VGroup(
            HSplit(
                UItem(
                    "available_bundles",
                    editor=ListStrEditor(
                        adapter=ListAdapter(),
                        selected="selected_bundle"),
                ),
                UItem('current_model', style='custom', editor=InstanceEditor())
            ),
            HGroup(
                UItem(
                    'add_button',
                    enabled_when="selected_bundle is not None"
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

    @on_trait_change("selected_bundle")
    def update_current_model(self):
        if self.selected_bundle is None:
            self.current_model = None
            return
        selected_bundle_id = id(self.selected_bundle)
        if self._models.get(selected_bundle_id) is None:
            model = self.selected_bundle.create_model()
            self._models[selected_bundle_id] = model
            self.current_model = model
        else:
            self.current_model = self._models.get(selected_bundle_id)
