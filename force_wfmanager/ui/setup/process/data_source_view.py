from traits.api import (
    HasStrictTraits, Instance, List, Int, on_trait_change,
    Bool, HTML, Property, Event, Unicode, HasTraits,
    cached_property, Either
)
from traitsui.api import (
    View, Item, TableEditor, VGroup, TextEditor, UReadonly
)
from traitsui.table_column import ObjectColumn

from force_bdss.api import (
    BaseDataSourceModel, InputSlotInfo, OutputSlotInfo
)

from force_wfmanager.ui.ui_utils import (
    get_factory_name, get_default_background_color, retain_list)
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry)


class TableRow(HasStrictTraits):
    """ Base class representing attributes shared between Input and Output
    rows"""

    # -------------------
    # Required Attributes
    # -------------------

    #: Model of the evaluator, either type InputSlotInfo or
    #: OutputSlotInfo
    model = Either(Instance(InputSlotInfo),
                   Instance(OutputSlotInfo))

    #: Index of the slot in the slot list
    index = Int()

    #: Text to display in the Row UI
    text = Unicode()


#: The TraitsUI editor used for :object:`TableRow.model.name`
name_editor = TextEditor(auto_set=False,
                         enter_set=True)

#: The TraitsUI editor used for :class:`InputSlotRow`
#: and :class:`OutputSlotRow`
slots_editor = TableEditor(
    sortable=False,
    configurable=False,
    selected="selected_slot_row",
    columns=[
        ObjectColumn(name="index", label="", editable=False),
        ObjectColumn(name="model.type", label="Type", editable=False),
        ObjectColumn(name="model.name", label="Variable Name",
                     editable=True, editor=name_editor),
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

    #: Input slots representation for the table editor
    input_slot_rows = List(TableRow)

    #: Output slots representation for the table editor
    output_slot_rows = List(TableRow)

    # --------------------
    # Dependent Attributes
    # --------------------

    #: Currently selected slot in the table
    #: Listens to: :attr:`input_slots_editor`, :attr:`output_slots_editor`
    selected_slot_row = Instance(TableRow)

    #: Event to request a verification check on the workflow
    #: Listens to: :attr:`input_slot_rows.name
    #: <input_slot_rows>`, :attr:`output_slot_rows.name
    #: <output_slot_rows>`
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
                    "input_slot_rows",
                    label="Input variables",
                    editor=slots_editor,
                ),
                Item(
                    "output_slot_rows",
                    label="Output variables",
                    editor=slots_editor,
                ),
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

    # -------------------
    #     Defaults
    # -------------------

    def _label_default(self):
        return get_factory_name(self.model.factory)

    def _input_slot_rows_default(self):
        """Creates a list of TableRow objects to represent each element
        in model.input_slot_info"""
        return [
            TableRow(model=model, index=index, text='Input')
            for index, model in enumerate(self.model.input_slot_info)
        ]

    def _output_slot_rows_default(self):
        """Creates a list of TableRow objects to represent each element
        in model.output_slot_info"""
        return [
            TableRow(model=model, index=index, text="Output")
            for index, model in enumerate(self.model.output_slot_info)
        ]

    # -------------------
    #     Listeners
    # -------------------

    # Description update on UI selection change
    @cached_property
    def _get_selected_slot_description(self):
        if self.selected_slot_row is None:
            return DEFAULT_MESSAGE

        idx = self.selected_slot_row.index
        type_text = self.selected_slot_row.text
        row_type = self.selected_slot_row.model.type
        description = self.selected_slot_row.model.description

        return SLOT_DESCRIPTION.format(row_type, type_text, idx, description)

    @on_trait_change(
        'input_slot_rows.[model.[name,type]],'
        'output_slot_rows.[model.[name,type]]'
    )
    def data_source_change(self):
        """Fires :func:`verify_workflow_event` when an input slot or output
        slot is changed"""
        self.verify_workflow_event = True

    # Changed Slots Functions
    @on_trait_change('model:changes_slots')
    def _update_slots_tables(self):
        """Update input_slot_info and output_slot_info attributes to
        their defaults, based on the return value of a BaseDataSource
        slots method. Retains any InputSlotInfo or OutputSlotInfo elements
        that have been defined before."""

        # Get new slots, caused by change_slots event
        new_input_slot_info, new_output_slot_info = (
            self.model.slot_info_defaults()
        )

        # Update the input_slot_info and output_slot_info attributes
        # by retaining any slots that already exist and are named in the
        # UI
        self.model.input_slot_info = retain_list(
            new_input_slot_info, self.model.input_slot_info,
            ['type', 'description']
        )

        self.model.output_slot_info = retain_list(
            new_output_slot_info, self.model.output_slot_info,
            ['type', 'description']
        )

        # Assign new TableRows for each updated slot UI
        self._fill_slot_rows()

    # -------------------
    #   Private Methods
    # -------------------

    def _fill_slot_rows(self):
        """Fill the tables rows according to input_slot_info and
        output_slot_info on the model"""

        self.input_slot_rows = self._input_slot_rows_default()
        self.output_slot_rows = self._output_slot_rows_default()

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
