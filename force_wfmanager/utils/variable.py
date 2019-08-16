from traits.api import (
    List, Instance, on_trait_change, Property,
    Tuple, HasTraits, Int, Unicode, cached_property, Bool
)

from force_bdss.api import (
    Identifier, VerifierError, OutputSlotInfo
)
from force_bdss.local_traits import CUBAType

from force_wfmanager.ui.setup.process.data_source_view import (
    DataSourceView, InputSlotRow, OutputSlotRow

)


class Variable(HasTraits):
    """Class used to store UI input and output information from DataSources
    as individual variables. These are then selected by the MCO optimiser as
    possible parameters or KPIs"""

    # ------------------
    # Regular Attributes
    # ------------------

    #: DataSourceView that contains Variable as an output
    origin = Instance(DataSourceView)

    #: The index of the layer the origin data source belongs to.
    layer_index = Int()

    #: DataSource OutputSlotRow that is used to update Variable name
    output_slot_row = Instance(OutputSlotRow)

    #: List of InputSlotRows referring to Variable
    input_slot_rows = List(Tuple(Int, InputSlotRow))

    # ---------------------
    # Dependent Attributes
    # ---------------------

    #: Name of Variable, listens to output_slot_info if updated by UI
    name = Identifier()

    #: CUBA type of Variable, listens to output_slot_row if updated by UI
    type = CUBAType()

    # ------------------
    #     Properties
    # ------------------

    #: DataSource OutputSlotRow that is used to update Variable name
    output_slot_info = Property(Instance(OutputSlotInfo),
                                depends_on='output_slot_row')

    #: Human readable label for class
    label = Property(Unicode, depends_on='name,type')

    #: Quick reference to check whether this Variable has any assigned
    #: input or output slots
    empty = Property(Bool, depends_on='output_slot_row,input_slot_rows')

    # ------------------
    #     Listeners
    # ------------------

    @cached_property
    def _get_label(self):
        return f'{self.type} {self.name}'

    @cached_property
    def _get_output_slot_info(self):
        if self.output_slot_row is not None:
            return self.output_slot_row.model

    @cached_property
    def _get_empty(self):
        """Checks whether not output slots or input slots have been hooked
        up to this Variable"""

        output_check = self.output_slot_row is None
        input_check = len(self.input_slot_rows) == 0

        return output_check and input_check

    @on_trait_change('name,output_slot_info.name')
    def sync_name(self):
        """Syncs to output_slot if assigned"""
        if self.output_slot_info is not None:
            self.name = self.output_slot_info.name

        if self.name == '':
            self.reset_variable()

    @on_trait_change('type,output_slot_row.type')
    def sync_type(self):
        """Syncs to output_row if assigned"""
        if self.output_slot_row is not None:
            self.type = self.output_slot_row.type

    @on_trait_change('name,type')
    def update_input_slots(self):
        """Syncs variable name and type to hooked up input slots"""
        for input_slot in self.input_slot_rows:
            input_slot[1].model.name = self.name
            input_slot[1].type = self.type

    @on_trait_change('output_slot_row,input_slot_rows[]')
    def update_slot_row_status(self):
        """Updates output_slot_row and all input_slot_rows with Variable
        hooked-up status"""

        if self.output_slot_row is not None:
            self.output_slot_row.status = True
            for input_slot in self.input_slot_rows:
                input_slot[1].status = True

    # ------------------
    #   Public Methods
    # ------------------

    def reset_variable(self):
        """Unhooks all input and output slots"""
        self.output_slot_row = None
        self.origin = None
        self.input_slot_rows = []

    def check_input_slot_hook(self, index, input_slot_row):
        """Check whether an input slot should be hooked up or removed from the
        Variable

        Parameters
        ----------
        index: int
            The index of the execution layer that the input_slot resides in
        input_slot_row: InputSlotRow
            A UI object from which the name of a variable is set by the user
        """

        name_check = self.name == input_slot_row.model.name
        type_check = self.type == input_slot_row.type

        # If the input slot name and type matches the Variable, hooked it up
        if name_check and type_check:
            if (index, input_slot_row) not in self.input_slot_rows:
                self.input_slot_rows.append((index, input_slot_row))
            return True

        # Else remove it if it has been hooked up previously
        if (index, input_slot_row) in self.input_slot_rows:
            self.input_slot_rows.remove((index, input_slot_row))
        return False

    def verify(self):
        """Reports a validation warning if variable is used as
        an input before being generated by an output slot
        """

        errors = []

        # Only perform check if Variable is being created by a
        # DataSource and has a defined name
        if self.output_slot_row is not None:
            for layer, slot in self.input_slot_rows:
                if layer <= self.layer_index:
                    errors.append(
                        VerifierError(
                            subject=slot.model,
                            local_error=('Variable is being used as an '
                                         'input before being generated as'
                                         ' an output'),
                            global_error=('A variable is being used as an '
                                          'input before being generated as'
                                          ' an output')
                        )
                    )

        return errors
