from traits.api import (HasStrictTraits, Instance, Str, List, Int,
                        on_trait_change, Either, Enum, Bool)

from traitsui.api import View, Item, ModelView, TableEditor
from traitsui.table_column import ObjectColumn

from force_bdss.api import (
    BaseDataSourceModel, BaseDataSource,
    BaseKPICalculatorModel, BaseKPICalculator,
    Identifier)
from force_bdss.core.input_slot_map import InputSlotMap

from .view_utils import get_factory_name


class TableRow(HasStrictTraits):
    #: Type of the slot
    type = Str()

    #: Index of the slot in the slot list
    index = Int()

    #: Model of the evaluator
    model = Either(
        Instance(BaseDataSourceModel),
        Instance(BaseKPICalculatorModel),
        allow_none=False,
    )

    def __init__(self, model, *args, **kwargs):
        self.model = model

        super(TableRow, self).__init__(*args, **kwargs)


class InputSlotRow(TableRow):
    #: Name of the slot
    name = Enum(values='_combobox_values')

    #: Available variables as input for this evaluator
    available_variables = List(Identifier)

    #: Possible values for the name of the input, it can be an empty string or
    #: one of the available variables
    _combobox_values = List(Identifier)

    @on_trait_change('name')
    def update_model(self):
        self.model.input_slot_maps[self.index].name = self.name

    @on_trait_change('available_variables')
    def update_available_variables(self):
        self._combobox_values = [''] + self.available_variables
        self.name = ('' if self.name not in self.available_variables
                     else self.name)

    def __combobox_values_default(self):
        return [''] + self.available_variables


class OutputSlotRow(TableRow):
    #: Name of the slot
    name = Identifier()

    @on_trait_change('name')
    def update_model(self):
        self.model.output_slot_names[self.index] = self.name


slots_editor = TableEditor(
    sortable=False,
    configurable=False,
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

    #: Available variables for the input slots
    available_variables = List(Identifier)

    #: The human readable name of the evaluator
    label = Str()

    #: evaluator object, shouldn't be touched
    _evaluator = Either(
        Instance(BaseDataSource),
        Instance(BaseKPICalculator),
    )

    #: Input slots representation for the table editor
    input_slots_representation = List(InputSlotRow)

    #: Output slots representation for the table editor
    output_slots_representation = List(OutputSlotRow)

    #: Defines if the evaluator is valid or not
    valid = Bool(True)

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

        self._create_slots_tables()

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
                .format(type(self.model).__name__))

    def _create_slots_tables(self):
        """ Initialize the tables for editing the input and output slots

        Raises
        ------
        RuntimeError:
            If the input slots or output slots in the model are not of the
            right length. This can come from a corrupted file.
        """
        input_slots, output_slots = self._evaluator.slots(self.model)

        # Initialize model.input_slot_maps if not initialized yet
        if len(self.model.input_slot_maps) == 0:
            self.model.input_slot_maps = [
                InputSlotMap(name='') for _ in input_slots
            ]

        if len(self.model.input_slot_maps) != len(input_slots):
            raise RuntimeError(
                "The number of input slots ({}) of the {} model doesn't match "
                "the expected number of slots ({}). This is likely due to a "
                "corrupted file."
                .format(
                    len(self.model.input_slot_maps),
                    type(self.model).__name__,
                    len(input_slots)))

        # Initialize model.output_slot_names if not initialized yet
        if len(self.model.output_slot_names) == 0:
            self.model.output_slot_names = len(output_slots)*['']

        if len(self.model.output_slot_names) != len(output_slots):
            raise RuntimeError(
                "The number of output slots ({}) of the {} model doesn't "
                "match the expected number of slots ({}). This is likely due "
                "to a corrupted file."
                .format(
                    len(self.model.output_slot_names),
                    type(self.model).__name__,
                    len(output_slots)))

        self._fill_slot_rows(input_slots, output_slots)

    @on_trait_change('model.changes_slots')
    def _update_slots_tables(self):
        """ Update the tables of slots when a change on the model triggers a
        change on the shape of the input/output slots """
        input_slots, output_slots = self._evaluator.slots(self.model)

        #: Initialize the input slots
        self.model.input_slot_maps = []
        for input_slot in input_slots:
            self.model.input_slot_maps.append(InputSlotMap(name=''))

        #: Initialize the output slots
        self.model.output_slot_names = len(output_slots)*['']

        self._fill_slot_rows(input_slots, output_slots)

    def _fill_slot_rows(self, input_slots, output_slots):
        """ Fill the tables rows according to input_slots and output_slots
        needed by the evaluator and the model slot values """
        self.input_slots_representation = [
            InputSlotRow(model=self.model,
                         available_variables=self.available_variables,
                         index=index,
                         name=self.model.input_slot_maps[index].name,
                         type=input_slot.type)
            for index, input_slot in enumerate(input_slots)
        ]

        self.output_slots_representation = [
            OutputSlotRow(model=self.model,
                          index=index,
                          name=self.model.output_slot_names[index],
                          type=output_slot.type)
            for index, output_slot in enumerate(output_slots)
        ]

    @on_trait_change('available_variables')
    def update_input_rows(self):
        for input_slot_row in self.input_slots_representation:
            input_slot_row.available_variables = self.available_variables
