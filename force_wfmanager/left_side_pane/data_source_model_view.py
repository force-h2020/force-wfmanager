from traits.api import Instance, Str, List, Property, Dict

from traitsui.api import View, Item, ModelView

from force_bdss.api import BaseDataSourceModel

from .view_utils import get_factory_name


class DataSourceModelView(ModelView):
    #: DataSource model
    model = Instance(BaseDataSourceModel, allow_none=False)

    #: The human readable name of the Data Source
    label = Str()

    #: The input slot maps which is a list of dictionary defining the input
    #: slots of the data source model
    input_slot_maps = Property(
        List(Dict),
        depends_on='model.input_slot_maps'
    )

    #: The output list defining the output names of the data source
    output_slot_names = Property(
        List(Str),
        depends_on='model.output_slot_names'
    )

    #: Base view for the Data Source
    traits_view = View(
        Item(name="input_slot_maps"),
        Item(name="output_slot_names"),
        kind="subpanel",
    )

    def _label_default(self):
        return get_factory_name(self.model.factory)

    def _get_input_slot_maps(self):
        return self.model.input_slot_maps

    def _get_output_slot_names(self):
        return self.model.output_slot_names
