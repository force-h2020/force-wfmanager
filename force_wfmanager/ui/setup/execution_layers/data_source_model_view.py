from traits.api import (HasStrictTraits, Instance, List, Int,
                        on_trait_change, Enum, Bool, HTML, Property,
                        Either, Event, Unicode)

from traitsui.api import (View, Item, ModelView, TableEditor, VGroup,
                          TextEditor, UReadonly)
from traitsui.table_column import ObjectColumn

from force_bdss.api import (BaseDataSourceModel, BaseDataSource, Identifier,
                            InputSlotInfo, OutputSlotInfo)

from force_wfmanager.ui.ui_utils import (
    get_factory_name, get_default_background_color)
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry)


class TableRow(HasStrictTraits):
    """ Base class representing attributes shared between Input and Output
    rows"""
    # -------------------
    # Required Attributes
    # -------------------

    #: Type of the slot
    type = Unicode()

    #: Index of the slot in the slot list
    index = Int()

    #: Model of the evaluator
    model = Instance(BaseDataSourceModel)

    # ------------------
    # Regular Attributes
    # ------------------

    #: A human readable description of the slot
    description = Unicode()

    def __init__(self, model, *args, **kwargs):
        self.model = model
        super(TableRow, self).__init__(*args, **kwargs)


class InputSlotRow(TableRow):
    """Row in the UI representing DataSource inputs. """
    # -------------------
    # Required Attributes
    # -------------------

    #: Available variables as input for this evaluator
    available_variables = List(Identifier)

    # ------------------
    # Derived Attributes
    # ------------------

    #: Name of the slot.
    #: Listens to: :attr:`model.input_slot_info.name <TableRow.model>`
    name = Enum(values='_combobox_values')

    #: Possible values for the name of the input, it can be an empty string or
    #: one of the available variables
    #: Listens to: :attr:`available_variables`
    _combobox_values = List(Identifier)

    @on_trait_change('model.input_slot_info.name')
    def update_view(self):
        """Synchronises the InputSlotRow with the underlying model"""
        self.name = self.model.input_slot_info[self.index].name

    @on_trait_change('name')
    def update_model(self):
        """Synchronises the model if the user changes a model object's name
        via the UI
        """
        self.model.input_slot_info[self.index].name = self.name

    @on_trait_change('available_variables')
    def update_combobox_values(self):
        """Updates the values shown in the dropdown menu in the UI when the
        list of available variables changes
        """
        self._combobox_values = [''] + self.available_variables
        self.name = ('' if self.name not in self.available_variables
                     else self.name)

    def __combobox_values_default(self):
        return [''] + self.available_variables


class OutputSlotRow(TableRow):

    # ------------------
    # Derived Attributes
    # ------------------

    #: Name of the slot
    #: Listens to: :attr:`model.output_slot_info.name <TableRow.model>`
    name = Identifier()

    @on_trait_change('model.output_slot_info[]')
    def update_view(self):
        """ Synchronises the OutputSlotRow with the underlying model"""
        self.name = self.model.output_slot_info[self.index].name

    @on_trait_change('name')
    def update_model(self):
        """ Synchronises the model if the user changes a model object's name
        via the UI
        """
        self.model.output_slot_info[self.index].name = self.name


#: The TraitsUI editor used for :class:`InputSlotRow`
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

#: The TraitsUI editor used for :class:`OutputSlotRow`
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

    # -------------------
    # Required Attributes
    # -------------------

    #: Model of the evaluator (More restrictive than the ModelView model
    #: attribute)
    model = Instance(BaseDataSourceModel)

    #: The index of the layer this data source belongs to.
    layer_index = Int()

    #: Registry of the available variables
    variable_names_registry = Instance(VariableNamesRegistry)

    # ------------------
    # Regular Attributes
    # ------------------

    #: The human readable name of the data source
    label = Unicode()

    #: evaluator object, shouldn't be touched
    _data_source = Instance(BaseDataSource)

    #: Input slots representation for the table editor
    input_slots_representation = List(InputSlotRow)

    #: Output slots representation for the table editor
    output_slots_representation = List(OutputSlotRow)

    # --------------------
    # Dependent Attributes
    # --------------------

    #: Currently selected slot in the table
    #: Listens to: :attr:`input_slots_editor`, :attr:`output_slots_editor`
    selected_slot_row = Either(Instance(InputSlotRow), Instance(OutputSlotRow))

    #: Event to request a verification check on the workflow
    #: Listens to: :attr:`input_slots_representation.name
    #: <input_slots_representation>`, :attr:`output_slots_representation.name
    #: <output_slots_representation>`
    verify_workflow_event = Event

    #: Defines if the evaluator is valid or not. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    valid = Bool(True)

    #: An error message for issues in this modelview. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    error_message = Unicode()

    # ----------
    # Properties
    # ----------

    #: HTML for the selected slot description
    selected_slot_description = Property(HTML, depends_on="selected_slot_row")

    # ----
    # View
    # ----

    #: Base view for the evaluator
    traits_view = View(
        VGroup(
            VGroup(
                Item(
                    "input_slots_representation",
                    label="Input variables",
                    editor=input_slots_editor,
                ),
                Item(
                    "output_slots_representation",
                    label="Output variables",
                    editor=output_slots_editor,
                )
            ),
            VGroup(
                UReadonly(
                    "selected_slot_description",
                    editor=TextEditor(),
                    ),
                label="Selected parameter description",
                show_border=True
            ),
        ),
    )

    def __init__(self, model, variable_names_registry, *args, **kwargs):
        self.model = model
        self.variable_names_registry = variable_names_registry

        super(DataSourceModelView, self).__init__(*args, **kwargs)

        self._create_slots_tables()

    # Initialization

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

    def _fill_slot_rows(self, input_slots, output_slots):
        """ Fill the tables rows according to input_slots and output_slots
        needed by the evaluator and the model slot values """
        available_variables = self._available_variables()
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

    # Defaults

    def _label_default(self):
        return get_factory_name(self.model.factory)

    def __data_source_default(self):
        return self.model.factory.create_data_source()

    @on_trait_change(
        'input_slots_representation.name,output_slots_representation.name'
    )
    def data_source_change(self):
        """Fires :func:`verify_workflow_event` when an input slot or output
        slot is changed"""
        self.verify_workflow_event = True

    # Changed Slots Functions

    @on_trait_change('model.changes_slots')
    def _update_slots_tables(self):
        """ Update the tables of slots when a change on the model triggers a
        change on the shape of the input/output slots"""
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

    # Avaliable Variables Functions

    @on_trait_change(
        'variable_names_registry.available_variables[],'
        'output_slots_representation.name,output_slots_representation.type,'
        'input_slots_representation.name,input_slots_representation.type'
    )
    def update_data_source_input_rows(self):
        """Updates the available variables attribute for any InputSlotRow
        of this data source"""
        for input_slot_row in self.input_slots_representation:
            available_variables = self._available_variables_by_type(
                input_slot_row.type)
            input_slot_row.available_variables = available_variables

    def _available_variables(self):
        """Returns the available variables for the containing execution layer
        of this data source
        """
        registry = self.variable_names_registry
        idx = self.layer_index

        return registry.available_variables[idx]

    def _available_variables_by_type(self, variable_type):
        """Returns the available variables of variable_type for the
        containing execution layer of this data source

        Parameters
        ----------
        variable_type: CUBAType
            Searches for available variables of this type
        """
        registry = self.variable_names_registry
        idx = self.layer_index
        if variable_type in registry.available_variables_by_type[idx]:
            return registry.available_variables_by_type[idx][variable_type]
        return []

    # Model change functions

    @on_trait_change('model.input_slot_info.name,model.output_slot_info.name')
    def update_slot_info_names(self):
        """Updates the name displayed in a Input/OutputSlotRow if the name
        changes in the model.
        """
        for info, row in zip(self.model.input_slot_info,
                             self.input_slots_representation):
            row.name = info.name

        for info, row in zip(self.model.output_slot_info,
                             self.output_slots_representation):
            row.name = info.name

    # Description update on UI selection change

    def _get_selected_slot_description(self):
        if self.selected_slot_row is None:
            return DEFAULT_MESSAGE

        idx = self.selected_slot_row.index
        row_type = self.selected_slot_row.type
        description = self.selected_slot_row.description

        type_text = (
            "Input" if isinstance(self.selected_slot_row, InputSlotRow)
            else "Output")
        return SLOT_DESCRIPTION.format(row_type, type_text, idx, description)


BACKGROUND_COLOR = get_default_background_color()


SLOT_DESCRIPTION = """
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style type="text/css">
            .container{{
                width: 100%;
                font-family: sans-serif;
                display: block;
            }}
        </style>
    </head>
    <body>
        <h2>{}</h2>
        <h4>{} row {}</h4>
        <p>{}</p>
    </body>
    </html>
    """

DEFAULT_MESSAGE = """
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style type="text/css">
            .container{{
                width: 100%;
                font-family: sans-serif;
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
