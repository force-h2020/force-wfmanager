from traits.api import (HasStrictTraits, Instance, Str, List, Int,
                        on_trait_change, Either)

from traitsui.api import View, Item, UItem, ModelView, TableEditor
from traitsui.table_column import ObjectColumn

from force_bdss.api import (
    BaseDataSourceModel, BaseDataSource,
    BaseKPICalculatorModel, BaseKPICalculator)

from .view_utils import get_factory_name


class OutputSlot(HasStrictTraits):
    #: Type of the slot
    type = Str()

    #: Name of the slot
    name = Str()

    #: Index of the slot in the slot list
    index = Int()

    #: Model of the evaluator
    model = Either(
        Instance(BaseDataSourceModel, allow_none=False),
        Instance(BaseKPICalculatorModel, allow_none=False),
    )

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


class EvaluatorModelView(ModelView):
    #: Model of the evaluator (More restrictive than the ModelView model
    #: attribute)
    model = Either(
        Instance(BaseDataSourceModel, allow_none=False),
        Instance(BaseKPICalculatorModel, allow_none=False),
    )

    #: The human readable name of the evaluator
    label = Str()

    #: Data source object, shouldn't be touched
    _evaluator = Either(
        Instance(BaseDataSource),
        Instance(BaseKPICalculator),
    )

    #: Output slots representation for the table editor
    output_slots_representation = List(OutputSlot)

    #: Base view for the evaluator
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
        if isinstance(model, BaseDataSourceModel):
            self._evaluator = model.factory.create_data_source()
        elif isinstance(model, BaseKPICalculatorModel):
            self._evaluator = model.factory.create_kpi_calculator()

        self._update_output_slots_table()

        super(EvaluatorModelView, self).__init__(*args, **kwargs)

    def _label_default(self):
        return get_factory_name(self.model.factory)

    @on_trait_change('model.changes_slots')
    def _update_output_slots_table(self):
        _, output_slots = self._evaluator.slots(self.model)

        #: Initialize the output_slot_names in the model
        self.model.output_slot_names = len(output_slots)*['']

        # Initialize slot names representation for the tables
        self.output_slots_representation = [
            OutputSlot(type=output_slot.type, model=self.model, index=index)
            for index, output_slot in enumerate(output_slots)
        ]
