from traits.api import (HasStrictTraits, Instance, Str, List, Int,
                        on_trait_change, Enum, Bool)

from traitsui.api import View, Item, ModelView, TableEditor
from traitsui.table_column import ObjectColumn

from force_bdss.api import (
    BaseDataSourceModel, BaseDataSource,
    Identifier)
from force_bdss.core.input_slot_info import InputSlotInfo
from force_bdss.core.output_slot_info import OutputSlotInfo

from .view_utils import get_factory_name
from .variable_names_registry import VariableNamesRegistry


class TableRow(HasStrictTraits):
    #: Type of the slot
    type = Str()

    #: Index of the slot in the slot list
    index = Int()

    #: Model of the evaluator
    model = Instance(BaseDataSourceModel)

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

    @on_trait_change('model.input_slot_info.name')
    def update_view(self):
        self.name = self.model.input_slot_info[self.index].name

    @on_trait_change('name')
    def update_model(self):
        self.model.input_slot_info[self.index].name = self.name

    @on_trait_change('available_variables')
    def update_combobox_values(self):
        self._combobox_values = [''] + self.available_variables
        self.name = ('' if self.name not in self.available_variables
                     else self.name)

    def __combobox_values_default(self):
        return [''] + self.available_variables


class OutputSlotRow(TableRow):
    #: Name of the slot
    name = Identifier()

    @on_trait_change('model.output_slot_info[]')
    def update_view(self):
        self.name = self.model.output_slot_info[self.index].name

    @on_trait_change('name')
    def update_model(self):
        self.model.output_slot_info[self.index].name = self.name


slots_editor = TableEditor(
    sortable=False,
    configurable=False,
    columns=[
        ObjectColumn(name="index", label="", editable=False),
        ObjectColumn(name="type", label="Type", editable=False),
        ObjectColumn(name="name", label="Variable Name", editable=True),
    ]
)


class DataSourceModelView(ModelView):
    #: Model of the evaluator (More restrictive than the ModelView model
    #: attribute)
    model = Instance(BaseDataSourceModel)

    #: Link to the containing layer
    execution_layer_mv = Instance(
        'force_wfmanager.left_side_pane'
        '.execution_layer_model_view.ExecutionLayerModelView'
    )

    #: Registry of the available variables
    variable_names_registry = Instance(VariableNamesRegistry)

    #: The human readable name of the evaluator
    label = Str()

    #: evaluator object, shouldn't be touched
    _data_source = Instance(BaseDataSource)

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

        super(DataSourceModelView, self).__init__(*args, **kwargs)

        self._create_slots_tables()

    def _label_default(self):
        return get_factory_name(self.model.factory)

    def _create_slots_tables(self):
        """ Initialize the tables for editing the input and output slots

        Raises
        ------
        RuntimeError:
            If the input slots or output slots in the model are not of the
            right length. This can come from a corrupted file.
        """
        input_slots, output_slots = self._data_source.slots(self.model)

        # Initialize model.input_slot_info if not initialized yet
        if len(self.model.input_slot_info) == 0:
            self.model.input_slot_info = [
                InputSlotInfo(name='') for _ in input_slots
            ]

        if len(self.model.input_slot_info) != len(input_slots):
            raise RuntimeError(
                "The number of input slots ({}) of the {} model doesn't match "
                "the expected number of slots ({}). This is likely due to a "
                "corrupted file."
                .format(
                    len(self.model.input_slot_info),
                    type(self.model).__name__,
                    len(input_slots)))

        # Initialize model.output_slot_info if not initialized yet
        if len(self.model.output_slot_info) == 0:
            self.model.output_slot_info = [
                OutputSlotInfo(name="") for _ in output_slots
            ]

        if len(self.model.output_slot_info) != len(output_slots):
            raise RuntimeError(
                "The number of output slots ({}) of the {} model doesn't "
                "match the expected number of slots ({}). This is likely due "
                "to a corrupted file."
                .format(
                    len(self.model.output_slot_info),
                    type(self.model).__name__,
                    len(output_slots)))

        self._fill_slot_rows(input_slots, output_slots)

    @on_trait_change('model.changes_slots')
    def _update_slots_tables(self):
        """ Update the tables of slots when a change on the model triggers a
        change on the shape of the input/output slots """
        #: This synchronization maybe is something that should be moved to the
        #: model.
        self.input_slots_representation[:] = []
        self.output_slots_representation[:] = []

        input_slots, output_slots = self._data_source.slots(self.model)

        #: Initialize the input slots
        self.model.input_slot_info = [
            InputSlotInfo(name='')
            for _ in input_slots
        ]

        #: Initialize the output slots
        self.model.output_slot_info = len(output_slots)*['']

        self._fill_slot_rows(input_slots, output_slots)

    def _fill_slot_rows(self, input_slots, output_slots):
        """ Fill the tables rows according to input_slots and output_slots
        needed by the evaluator and the model slot values """
        available_variables = self._get_available_variables()

        self.input_slots_representation = [
            InputSlotRow(model=self.model,
                         available_variables=available_variables,
                         index=index,
                         name=self.model.input_slot_info[index].name,
                         type=input_slot.type)
            for index, input_slot in enumerate(input_slots)
        ]

        self.output_slots_representation = [
            OutputSlotRow(model=self.model,
                          index=index,
                          name=self.model.output_slot_info[index].name,
                          type=output_slot.type)
            for index, output_slot in enumerate(output_slots)
        ]

    def __data_source_default(self):
        return self.model.factory.create_data_source()

    @on_trait_change('variable_names_registry.available_variables[]')
    def update_data_source_input_rows(self):
        available_variables = self._get_available_variables()
        for input_slot_row in self.input_slots_representation:
            input_slot_row.available_variables = available_variables

    def _get_available_variables(self):
        index = self._get_layer_index()
        return self.variable_names_registry.available_variables[index]

    def _get_layer_index(self):
        return self.execution_layer_mv.layer_index()
