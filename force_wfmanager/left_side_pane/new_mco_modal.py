from traits.api import (HasStrictTraits, Instance, List, Button,
                        on_trait_change, Dict)
from traitsui.api import (View, Handler, HSplit, VGroup, UItem,
                          HGroup, ListStrEditor)

from force_bdss.api import BaseMCOModel, BaseMultiCriteriaOptimizerBundle
from force_bdss.workspecs.workflow import Workflow

from .view_utils import ListAdapter


class ModalHandler(Handler):
    def object_add_mco_button_changed(self, info):
        if info.object.current_model is not None:
            info.object.workflow.multi_criteria_optimizer = \
                info.object.current_model
        info.ui.dispose(True)
        info.object.clear_model()

    def object_cancel_button_changed(self, info):
        info.ui.dispose(False)
        info.object.clear_model()


class NewMCOModal(HasStrictTraits):
    """ Dialog which allows the user to add a new MCO to the workflow
    """
    workflow = Instance(Workflow)

    #: Available MCO bundles
    available_mcos = List(BaseMultiCriteriaOptimizerBundle)

    #: Selected MCO bundle in the list of MCOs
    selected_mco = Instance(BaseMultiCriteriaOptimizerBundle)

    add_mco_button = Button("Add")
    cancel_button = Button('Cancel')

    _models = Dict()

    current_model = Instance(BaseMCOModel)

    traits_view = View(
        VGroup(
            HSplit(
                UItem(
                    "available_mcos",
                    editor=ListStrEditor(
                        adapter=ListAdapter(),
                        selected="selected_mco"),
                ),
                UItem('current_model', style='custom')
            ),
            HGroup(
                UItem(
                    'add_mco_button',
                    enabled_when="selected_mco is not None"
                ),
                UItem('cancel_button')
            )
        ),
        title='New MCO',
        handler=ModalHandler(),
        width=800,
        height=600,
        kind="livemodal"
    )

    def clear_model(self):
        self.selected_mco = None
        self.current_model = None
        self._models = {}

    @on_trait_change("selected_mco")
    def update_current_model(self):
        if self.selected_mco is None:
            return
        selected_mco_id = id(self.selected_mco)
        if self._models.get(selected_mco_id) is None:
            model = self.selected_mco.create_model()
            self._models[selected_mco_id] = model
            self.current_model = model
        else:
            self.current_model = self._models.get(selected_mco_id)
