from traits.api import (HasStrictTraits, Instance, List, Button,
                        on_trait_change, Dict)
from traitsui.api import (View, Handler, HSplit, VGroup, UItem,
                          HGroup, ListStrEditor)
from traitsui.list_str_adapter import ListStrAdapter

from force_bdss.api import BaseDataSourceModel, BaseDataSourceBundle
from force_bdss.workspecs.workflow import Workflow


def get_bundle_name(bundle):
    """ Returns a bundle name, given the bundle. This ensure that something
    will be displayed (id or name of the bundle) even if no name has been
    specified for the bundle """
    name = bundle.name.strip()
    if len(name) != 0:
        return name
    else:
        return bundle.id


class ListAdapter(ListStrAdapter):
    """ Adapter for the list of available MCOs/Data sources/KPI calculators
    bundles """
    def get_text(self, object, trait, index):
        return get_bundle_name(self.item)


class ModalHandler(Handler):
    def object_add_data_source_button_changed(self, info):
        if info.object.current_model is not None:
            info.object.workflow.data_sources.append(
                info.object.current_model
            )
        info.ui.dispose(True)

    def object_cancel_button_changed(self, info):
        info.ui.dispose(False)


class NewDataSourceModal(HasStrictTraits):
    """ Dialog which allows the user to add a new DataSource to the workflow
    """
    workflow = Instance(Workflow)

    #: Available data source bundles
    available_data_sources = List(BaseDataSourceBundle)

    #: Selected data source bundle in the list of data sources
    selected_data_source = Instance(BaseDataSourceBundle)

    add_data_source_button = Button("Add")
    cancel_button = Button('Cancel')

    _models = Dict()

    current_model = Instance(BaseDataSourceModel)

    traits_view = View(
        VGroup(
            HSplit(
                UItem(
                    "available_data_sources",
                    editor=ListStrEditor(
                        adapter=ListAdapter(),
                        selected="selected_data_source"),
                ),
                UItem('current_model', style='custom')
            ),
            HGroup(
                UItem('add_data_source_button'),
                UItem('cancel_button')
            )
        ),
        title='New Data Source',
        handler=ModalHandler(),
        kind="livemodal"
    )

    @on_trait_change("selected_data_source")
    def update_current_model(self):
        selected_data_source_id = id(self.selected_data_source)
        if self._models.get(selected_data_source_id) is None:
            model = self.selected_data_source.create_model()
            self._models[selected_data_source_id] = model
            self.current_model = model
        else:
            self.current_model = self._models.get(selected_data_source_id)
