from traits.api import (HasStrictTraits, Instance, Str, List, Int,
                        on_trait_change)

from traitsui.api import View, Item, UItem, ModelView, TableEditor
from traitsui.table_column import ObjectColumn

from force_bdss.api import BaseDataSourceModel, BaseDataSource

from .view_utils import get_factory_name


class OutputSlot(HasStrictTraits):
    #: Type of the slot
    type = Str()

    #: Name of the slot
    name = Str()

    #: Index of the slot in the slot list
    index = Int()

    #: Model of the Data source
    model = Instance(BaseDataSourceModel, allow_none=False)

    @on_trait_change('name')
    def update_model(self):
        self.model.output_slot_names[self.index] = self.name


output_slots_editor = TableEditor(
    sortable=False,
    configurable=False,
    auto_size=False,
    columns=[
        ObjectColumn(name="type", label="Output", editable=False),
        ObjectColumn(name="name", label="Name", editable=True),
    ]
)


class DataSourceModelView(ModelView):
    #: DataSource model (More restrictive than the ModelView model attribute)
    model = Instance(BaseDataSourceModel, allow_none=False)

    #: The human readable name of the Data Source
    label = Str()

    #: Data source object, shouldn't be touched
    _data_source = Instance(BaseDataSource)

    #: Output slots representation for the table editor
    output_slots_representation = List(OutputSlot)

    #: Base view for the Data Source
    traits_view = View(
        Item("model.input_slot_maps"),
        UItem(
            "output_slots_representation",
            editor=output_slots_editor,
        ),
        kind="subpanel",
    )

    def __init__(self, model, *args, **kwargs):
        self.model = model
        self._data_source = model.factory.create_data_source()
        input_slots, output_slots = self._data_source.slots(self.model)

        #: Initialize the output_slot_names in the model
        self.model.output_slot_names = len(output_slots)*['']

        # Initialize slot names representation for the tables
        self.output_slots_representation = [
            OutputSlot(type=output_slot.type, model=self.model, index=index)
            for index, output_slot in enumerate(output_slots)
        ]

        super(DataSourceModelView, self).__init__(*args, **kwargs)

    def _label_default(self):
        return get_factory_name(self.model.factory)
