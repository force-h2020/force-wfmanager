from traits.api import (
    HasStrictTraits, Instance, List, Int, on_trait_change,
    Bool, HTML, Property, Event, Unicode, HasTraits,
    cached_property
)
from traitsui.api import (
    View, Item, TableEditor, VGroup, TextEditor, UReadonly
)
from traitsui.table_column import ObjectColumn

from force_bdss.api import (BaseDataSourceModel, BaseDataSource,
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

    # ------------------
    # Regular Attributes
    # ------------------

    #: A human readable description of the slot
    description = Unicode()


class InputSlotRow(TableRow):
    """Row in the UI representing DataSource inputs. """

    # -------------------
    # Required Attributes
    # -------------------

    #: Model of the evaluator
    model = Instance(InputSlotInfo)


class OutputSlotRow(TableRow):
    """Row in the UI representing DataSource outputs. """

    # -------------------
    # Required Attributes
    # -------------------

    #: Model of the evaluator
    model = Instance(OutputSlotInfo)


#: The TraitsUI editor used for :class:`InputSlotRow`
input_slots_editor = TableEditor(
    sortable=False,
    configurable=False,
    selected="selected_slot_row",
    columns=[
        ObjectColumn(name="index", label="", editable=False),
        ObjectColumn(name="type", label="Type", editable=False),
        ObjectColumn(name="model.name", label="Variable Name",
                     editable=True),
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
        ObjectColumn(name="model.name", label="Variable Name",
                     editable=True),
    ]
)


class DataSourceView(HasTraits):
    """A view for a single data source in a execution layer. Displays
    traits of BaseDataSourceModel and a tabular representation of the
    input / output variable slots"""

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

    #: evaluator object, used to generate slots containing type and description
    # of each variable (shouldn't be touched)
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
    selected_slot_row = Instance(TableRow)

    #: Event to request a verification check on the workflow
    #: Listens to: :attr:`input_slots_representation.name
    #: <input_slots_representation>`, :attr:`output_slots_representation.name
    #: <output_slots_representation>`
    verify_workflow_event = Event()

    #: Defines if the evaluator is valid or not. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    valid = Bool(True)

    #: An error message for issues in this modelview. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    error_message = Unicode()

    # ----------------
    #    Properties
    # ----------------

    #: HTML for the selected slot description
    selected_slot_description = Property(HTML, depends_on="selected_slot_row")

    # -------------
    #     View
    # -------------

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

    def __init__(self, *args, **kwargs):
        super(DataSourceView, self).__init__(*args, **kwargs)
        # Performs private method to set up slots tables on instantiation
        self._create_slots_tables()

    # -------------------
    #     Defaults
    # -------------------

    def _label_default(self):
        return get_factory_name(self.model.factory)

    def __data_source_default(self):
        return self.model.factory.create_data_source()

    # -------------------
    #     Listeners
    # -------------------

    # Description update on UI selection change
    @cached_property
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

    @on_trait_change(
        'input_slots_representation.[model.name,type],'
        'output_slots_representation.[model.name,type]'
    )
    def data_source_change(self):
        """Fires :func:`verify_workflow_event` when an input slot or output
        slot is changed"""
        self.verify_workflow_event = True

    # Changed Slots Functions
    @on_trait_change('model:changes_slots')
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
            InputSlotInfo(model=slot)
            for slot in input_slots
        ]

        #: Initialize the output slots
        self.model.output_slot_info = [
            OutputSlotInfo(name='')
            for _ in output_slots
        ]

        self._fill_slot_rows(input_slots, output_slots)

    # -------------------
    #   Private Methods
    # -------------------

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

        input_representations = []

        for index, input_slot in enumerate(input_slots):
            slot_representation = InputSlotRow(
                model=self.model.input_slot_info[index],
                index=index, type=input_slot.type,
                description=input_slot.description)
            input_representations.append(slot_representation)

        self.input_slots_representation[:] = input_representations

        output_representation = []

        for index, output_slot in enumerate(output_slots):
            slot_representation = OutputSlotRow(
                model=self.model.output_slot_info[index],
                index=index, type=output_slot.type,
                description=output_slot.description)
            output_representation.append(slot_representation)

        self.output_slots_representation[:] = output_representation

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
