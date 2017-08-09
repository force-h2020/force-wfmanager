from traits.api import (HasStrictTraits, Instance, Str, List, Int,
                        on_trait_change, Either)

from traitsui.api import View, Item, ModelView, TableEditor
from traitsui.table_column import ObjectColumn

from force_bdss.api import (
    BaseDataSourceModel, BaseDataSource,
    BaseKPICalculatorModel, BaseKPICalculator)
from force_bdss.core.input_slot_map import InputSlotMap

from .view_utils import get_factory_name


class InputSlot(HasStrictTraits):
    #: Type of the slot
    type = Str()

    #: Name of the slot
    name = Str()

    #: Index of the slot in the slot list
    index = Int()

    #: Model of the evaluator
    model = Either(
        Instance(BaseDataSourceModel),
        Instance(BaseKPICalculatorModel),
        allow_none=False,
    )

    @on_trait_change('name')
    def update_model(self):
        self.model.input_slot_maps[self.index].name = self.name


class OutputSlot(HasStrictTraits):
    #: Type of the slot
    type = Str()

    #: Name of the slot
    name = Str()

    #: Index of the slot in the slot list
    index = Int()

    #: Model of the evaluator
    model = Either(
        Instance(BaseDataSourceModel),
        Instance(BaseKPICalculatorModel),
        allow_none=False,
    )

    @on_trait_change('name')
    def update_model(self):
        self.model.output_slot_names[self.index] = self.name


slots_editor = TableEditor(
    sortable=False,
    configurable=False,
    auto_size=False,
    columns=[
        ObjectColumn(name="index", label="", editable=False),
        ObjectColumn(name="type", label="Type", editable=False),
        ObjectColumn(name="name", label="Variable Name", editable=True),
    ]
)


class EvaluatorModelView(ModelView):
    #: Model of the evaluator (More restrictive than the ModelView model
    #: attribute)
    model = Either(
        Instance(BaseDataSourceModel),
        Instance(BaseKPICalculatorModel),
        allow_none=False,
    )

    #: The human readable name of the evaluator
    label = Str()

    #: evaluator object, shouldn't be touched
    _evaluator = Either(
        Instance(BaseDataSource),
        Instance(BaseKPICalculator),
    )

    #: Input slots representation for the table editor
    input_slots_representation = List(InputSlot)

    #: Output slots representation for the table editor
    output_slots_representation = List(OutputSlot)

    #: Base view for the evaluator
    traits_view = View(
        Item(
            "input_slots_representation",
            label="Input variables",
            editor=slots_editor,
        ),
        Item(
            "output_slots_representation",
            label="Output variables",
            editor=slots_editor,
        ),
        kind="subpanel",
    )

    def __init__(self, model, *args, **kwargs):
        self.model = model

        super(EvaluatorModelView, self).__init__(*args, **kwargs)

        self._update_slots_tables()

    def _label_default(self):
        return get_factory_name(self.model.factory)

    def __evaluator_default(self):
        if isinstance(self.model, BaseDataSourceModel):
            return self.model.factory.create_data_source()
        elif isinstance(self.model, BaseKPICalculatorModel):
            return self.model.factory.create_kpi_calculator()
        else:
            raise TypeError(
                "The EvaluatorModelView needs a BaseDataSourceModel or a "
                "BaseKPICalculatorModel as model, but a {} has been given"
                .format(type(self.model).__name__)
            )

    @on_trait_change('model.changes_slots')
    def _update_slots_tables(self):
        input_slots, output_slots = self._evaluator.slots(self.model)

        #: Initialize the input slots
        self.model.input_slot_maps = []
        self.input_slots_representation = []
        for index, input_slot in enumerate(input_slots):
            self.model.input_slot_maps.append(InputSlotMap(name=''))
            self.input_slots_representation.append(
                InputSlot(index=index,
                          type=input_slot.type,
                          model=self.model)
            )

        #: Initialize the output slots
        self.model.output_slot_names = []
        self.output_slots_representation = []
        for index, output_slot in enumerate(output_slots):
            self.model.output_slot_names.append('')
            self.output_slots_representation.append(
                OutputSlot(index=index,
                           type=output_slot.type,
                           model=self.model)
            )
