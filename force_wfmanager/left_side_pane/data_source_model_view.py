from traits.api import (HasStrictTraits, Instance, Str, List, Int,
                        on_trait_change, Enum, Bool, HTML, Property,
                        Either, Event, Unicode)

from traitsui.api import View, Item, ModelView, TableEditor, HTMLEditor
from traitsui.table_column import ObjectColumn

from force_bdss.api import (BaseDataSourceModel, BaseDataSource, Identifier,
                            InputSlotInfo, OutputSlotInfo)

from .view_utils import get_factory_name, get_default_background_color
from .variable_names_registry import VariableNamesRegistry


class TableRow(HasStrictTraits):
    #: Type of the slot
    type = Str()

    #: Index of the slot in the slot list
    index = Int()

    #: Model of the evaluator
    model = Instance(BaseDataSourceModel)

    description = Unicode()

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
    def update_name(self):
        self.model.output_slot_info[self.index].name = self.name


input_slots_editor = TableEditor(
    sortable=False,
    configurable=False,
    selected="selected_slot_row",
    columns=[
        ObjectColumn(name="index", label="", editable=False),
        ObjectColumn(name="type", label="Type", editable=False),
        ObjectColumn(name="name", label="Variable Name", editable=True),
    ]
)

output_slots_editor = TableEditor(
    sortable=False,
    configurable=False,
    selected="selected_slot_row",
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

    #: The index of the layer this data source belongs to.
    layer_index = Int()

    #: evaluator object, shouldn't be touched
    _data_source = Instance(BaseDataSource)

    #: Input slots representation for the table editor
    input_slots_representation = List(InputSlotRow)

    #: Output slots representation for the table editor
    output_slots_representation = List(OutputSlotRow)

    #: Currently selected slot in the table
    selected_slot_row = Either(Instance(InputSlotRow), Instance(OutputSlotRow))

    #: HTML for the selected slot description
    selected_slot_description = Property(HTML, depends_on="selected_slot_row")

    #: Defines if the evaluator is valid or not
    valid = Bool(True)

    #: An error message for issues in this modelview
    error_message = Str()

    #: Event to request a verification check on the workflow
    verify_workflow_event = Event

    #: Base view for the evaluator
    traits_view = View(
        Item(
            "input_slots_representation",
            label="Input variables",
            editor=input_slots_editor,
        ),
        Item(
            "output_slots_representation",
            label="Output variables",
            editor=output_slots_editor,
        ),
        Item(
            "selected_slot_description",
            label="Description",
            editor=HTMLEditor(),
        ),
        kind="subpanel",
    )

    def __init__(self, model, variable_names_registry, *args, **kwargs):
        self.model = model
        self.variable_names_registry = variable_names_registry

        super(DataSourceModelView, self).__init__(*args, **kwargs)

        self._create_slots_tables()

    @on_trait_change('input_slots_representation.name,'
                     'output_slots_representation.name')
    def data_source_change(self):
        self.verify_workflow_event = True

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
        self.model.output_slot_info = [
            OutputSlotInfo(name='')
            for _ in output_slots
        ]

        self._fill_slot_rows(input_slots, output_slots)

    def _fill_slot_rows(self, input_slots, output_slots):
        """ Fill the tables rows according to input_slots and output_slots
        needed by the evaluator and the model slot values """
        available_variables = self._get_available_variables()

        input_representations = []

        for index, input_slot in enumerate(input_slots):
            slot_representation = InputSlotRow(model=self.model, index=index)
            new_name = self.model.input_slot_info[index].name
            if new_name not in available_variables:
                new_name = ''

            slot_representation.available_variables = available_variables
            slot_representation.name = new_name
            slot_representation.type = input_slot.type
            slot_representation.description = input_slot.description
            input_representations.append(slot_representation)

        self.input_slots_representation[:] = input_representations

        output_representation = []

        for index, output_slot in enumerate(output_slots):
            slot_representation = OutputSlotRow(model=self.model, index=index)
            slot_representation.name = self.model.output_slot_info[index].name
            slot_representation.type = output_slot.type
            slot_representation.description = output_slot.description

            output_representation.append(slot_representation)

        self.output_slots_representation[:] = output_representation

    def __data_source_default(self):
        return self.model.factory.create_data_source()

    @on_trait_change("model.input_slot_info.name,model.output_slot_info.name")
    def update_slot_info_names(self):
        for info, row in zip(self.model.input_slot_info,
                             self.input_slots_representation):
            row.name = info.name

        for info, row in zip(self.model.output_slot_info,
                             self.output_slots_representation):
            row.name = info.name

    @on_trait_change('variable_names_registry.available_variables[]')
    def update_data_source_input_rows(self):
        available_variables = self._get_available_variables()
        for input_slot_row in self.input_slots_representation:
            input_slot_row.available_variables = available_variables

    def _get_available_variables(self):
        registry = self.variable_names_registry
        return registry.available_variables[self.layer_index]

    def _get_selected_slot_description(self):
        if self.selected_slot_row is None:
            return DEFAULT_MESSAGE.format(BACKGROUND_COLOR)

        idx = self.selected_slot_row.index
        row_type = self.selected_slot_row.type
        description = self.selected_slot_row.description

        type_text = (
            "Input" if isinstance(self.selected_slot_row, InputSlotRow)
            else "Output")
        return SLOT_DESCRIPTION.format(
            BACKGROUND_COLOR, row_type, type_text, idx, description)


BACKGROUND_COLOR = get_default_background_color()


SLOT_DESCRIPTION = """
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style type="text/css">
            html{{
                background: {};
            }}
            .container{{
                width: 100%;
                display: block;
            }}
            .left-col{{
                width: 80%;
                display: inline-block;
                word-wrap: break-word;
            }}
            .right-col{{
                width: 15%;
                display: inline-block;
                word-wrap: break-word;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="left-col" w>
                <h2>{}</h2>
            </div>
            <div class="right-col">
                <h4>{} row {}</h4>
            </div>
            <p>{}</p>
        </div>
    </body>
    </html>
    """

DEFAULT_MESSAGE = """
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style type="text/css">
            html{{
                background: {};
            }}
            .container{{
                width: 100%;
                display: block;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <p> No Item Selected </p>
        </div>
    </body>
    </html>
    """
