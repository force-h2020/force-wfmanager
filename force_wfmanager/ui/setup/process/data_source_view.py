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

    #: Model of the evaluator
    model = Instance(HasStrictTraits)

    #: Index of the slot in the slot list
    index = Int()


class InputSlotRow(TableRow):
    """Row in the UI representing DataSource inputs. """

    # -------------------
    # Required Attributes
    # -------------------

    #: InputSlotInfo model of the evaluator
    model = Instance(InputSlotInfo)


class OutputSlotRow(TableRow):
    """Row in the UI representing DataSource outputs. """

    # -------------------
    # Required Attributes
    # -------------------

    #: OutputSlotInfo model of the evaluator
    model = Instance(OutputSlotInfo)


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
        ObjectColumn(name="model.index", label="", editable=False),
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
                    editor=slots_editor,
                ),
                Item(
                    "output_slots_representation",
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

    def __init__(self, *args, **kwargs):
        super(DataSourceView, self).__init__(*args, **kwargs)
        # Performs private method to set up slots tables on instantiation
        self._update_slots_tables()

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
        row_type = self.selected_slot_row.model.type
        description = self.selected_slot_row.model.description

        type_text = (
            "Input" if isinstance(self.selected_slot_row, InputSlotRow)
            else "Output")
        return SLOT_DESCRIPTION.format(row_type, type_text, idx, description)

    @on_trait_change(
        'input_slots_representation.[model.[name,type]],'
        'output_slots_representation.[model.[name,type]]'
    )
    def data_source_change(self):
        """Fires :func:`verify_workflow_event` when an input slot or output
        slot is changed"""
        self.verify_workflow_event = True

    # Changed Slots Functions
    @on_trait_change('model:changes_slots')
    def _update_slots_tables(self):
        """ Fill the tables rows according to input_slots and output_slots
        needed by the evaluator and the model slot values """

        self.input_slots_representation = [
            InputSlotRow(model=model, index=index)
            for index, model in enumerate(self.model.input_slot_info)
        ]

        self.output_slots_representation = [
            OutputSlotRow(model=model, index=index)
            for index, model in enumerate(self.model.output_slot_info)
        ]

    # -------------------
    #   Private Methods
    # -------------------

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
