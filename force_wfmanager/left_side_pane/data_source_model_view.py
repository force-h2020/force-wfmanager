from traits.api import Instance, Str

from traitsui.api import View, Item, ModelView

from force_bdss.api import BaseDataSourceModel

from .view_utils import get_factory_name


class DataSourceModelView(ModelView):
    #: DataSource model (More restrictive than the ModelView model attribute)
    model = Instance(BaseDataSourceModel, allow_none=False)

    #: The human readable name of the Data Source
    label = Str()

    #: Base view for the Data Source
    traits_view = View(
        Item("model.input_slot_maps"),
        Item("model.output_slot_names"),
        kind="subpanel",
    )

    def _label_default(self):
        return get_factory_name(self.model.factory)
