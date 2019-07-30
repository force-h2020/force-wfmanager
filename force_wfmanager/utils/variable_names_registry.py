import logging

from traits.api import (
    HasStrictTraits, List, Instance, on_trait_change, Property,
    cached_property, Dict, Tuple, HasTraits, Int, Unicode)

from force_bdss.api import (
    Identifier, Workflow, BaseDataSourceModel, OutputSlotInfo,
    InputSlotInfo, VerifierError
)
from force_bdss.local_traits import CUBAType

log = logging.getLogger(__name__)


class Variable(HasTraits):
    """Class used to store UI input and output information from DataSources
    as individual variables. These are then selected by the MCO optimiser as
    possible parameters or KPIs"""

    # -------------------
    # Required Attributes
    # -------------------

    # CUBA type of Variable
    type = CUBAType()

    # ------------------
    # Regular Attributes
    # ------------------

    # Layer index at which variable is generated
    layer = Int

    # DataSource that contains Variable as an output
    origin = Instance(BaseDataSourceModel)

    # DataSource output slot that is used to update Variable name
    origin_slot = Instance(OutputSlotInfo)

    # DataSources where Variable is used as an input
    input_slots = List(Tuple(Int, InputSlotInfo))

    # ---------------------
    # Dependent Attributes
    # ---------------------

    # Name of Variable, listens to origin_slot if updated by UI
    name = Identifier()

    # ------------------
    #     Properties
    # ------------------

    label = Property(Unicode, depends_on='origin_slot.name,type')

    def _get_label(self):
        return f'{self.type} {self.name}'

    @on_trait_change('origin_slot.name')
    def update_name(self):
        """If the origin output slot name is changed, update the
        variable name and all linked input slots"""
        self.name = self.origin_slot.name
        for input_slot in self.input_slots:
            input_slot[1].name = self.name

    @on_trait_change('input_slots,layer')
    def verify_generation(self):
        """Reports a validation warning if variable is used as
        an input before being generated
        """
        errors = []
        layer_check = True

        # Only perform check if Variable is being created by a
        # DataSource
        if self.origin is not None:
            for value in self.input_slots:
                if value[0] <= self.layer:
                    layer_check = False
                    break

        if not layer_check:
            errors.append(
                VerifierError(
                    subject=self,
                    global_error=('Variable is being used as an input'
                                  ' before being generated'),
                )
            )

        return errors


class VariableNamesRegistry(HasStrictTraits):
    """ Class used for listening to the structure of the Workflow in
    order to check the available variables that can be used as input_slots
    for each layer
    """

    # -------------------
    # Required Attributes
    # -------------------

    #: Workflow model
    workflow = Instance(Workflow, allow_none=False)

    # ------------------
    # Regular Attributes
    # ------------------

    #: Dictionary allowing the lookup of names associated with a chosen CUBA
    #: type.
    exec_layer_by_type = Dict(CUBAType, List(Variable))

    #: Dictionary allowing the lookup of names associated with a chosen CUBA
    #: type.
    variable_registry = Dict(Unicode, Variable)

    # -------------
    #   Properties
    # -------------

    #: A list of type lookup dictionaries, with one dictionary for each
    #: execution layer
    available_variables_by_type = Property(
        List(exec_layer_by_type),
        depends_on="variable_registry"
        )

    #: Same structure as available_output_variables_stack, but this contains
    #: the cumulated information. From the example above, this would contain::
    #:
    #:     [["Vol_A", "Vol_B"],
    #:      ["Vol_A", "Vol_B"],
    #:      ["Vol_A", "Vol_B", "Pressure_A"]]
    #:
    available_variables = Property(
        List(List(Variable)),
        depends_on="variable_registry"
    )

    def __init__(self, workflow, *args, **kwargs):
        super(VariableNamesRegistry, self).__init__(*args, **kwargs)
        self.workflow = workflow

    # ---------------
    #    Listeners
    # ---------------

    @cached_property
    def _get_available_variables(self):
        available_variables = [
            [] for _ in range(len(self.workflow.execution_layers))
        ]

        for variable in self.variable_registry.values():
            available_variables[variable.layer].append(variable.name)
            for slot in variable.input_slots:
                if slot[1].name not in available_variables[slot[0]]:
                    available_variables[slot[0]].append(slot[1].name)

        return available_variables

    def _get_available_variables_by_type(self):

        available_variables = [
            {} for _ in range(len(self.workflow.execution_layers))
        ]

        for variable in self.variable_registry.values():
            var_dict = available_variables[variable.layer]
            if variable.type in var_dict:
                var_dict[variable.type].append(variable)
            else:
                var_dict[variable.type] = [variable]

        return available_variables

    @on_trait_change(
        'workflow.execution_layers.data_sources.'
        '[input_slot_info.name,output_slot_info.name]'
    )
    def update_variable_registry(self):
        """Method takes information from DataSourceModel input and
        output slots, and compiles it into a dictionary containing a
        set of Variable objects. The keys to each Variable are mainly
        used for persistence checking cleanup purposes"""

        # List of keys referring to existing variables
        existing_variable_keys = []

        # List of references to variables with a defined origin
        output_variables = []

        for index, layer in enumerate(self.workflow.execution_layers):
            for data_source_model in layer.data_sources:
                # This try-except is also in execute.py in force_bdss,
                # so if this fails the workflow would not be able to run
                # anyway.
                # FIXME: Remove reliance on create_data_source(). If one
                # FIXME: datasource has an error, this shouldn't blow up
                # FIXME: the whole workflow. Especially during the setup
                # FIXME: phase!
                try:
                    data_source = (
                        data_source_model.factory.create_data_source())

                    # ds.slots() returns (input_slots, output_slots)
                    input_slots = data_source.slots(data_source_model)[0]
                    output_slots = data_source.slots(data_source_model)[1]
                except Exception:
                    log.exception(
                        "Unable to create data source from factory '{}' "
                        "in plugin '{}'. This may indicate a programming "
                        "error in the plugin".format(
                            data_source_model.factory.id,
                            data_source_model.factory.plugin.id))
                    raise

                for info, slot in zip(data_source_model.output_slot_info,
                                      output_slots):
                    # Key is reference to slot attribute on data_source_model.
                    # Therefore it is unique and exists as long as the slot
                    # exists
                    key = f'{id(info)}:{slot.type}'
                    existing_variable_keys.append(key)

                    # Only create the Variable if it has not been defined
                    # before this update
                    if key not in self.variable_registry.keys():
                        data = Variable(
                            type=slot.type,
                            layer=index,
                            origin_slot=info,
                            origin=data_source_model
                        )
                        self.variable_registry[key] = data

                    # Store a reference to the existing name and type of the
                    # Variable - this is used to cross check against possible
                    # input slots
                    ref = f'{info.name}:{slot.type}'
                    output_variables.append(ref)

                for info, slot in zip(data_source_model.input_slot_info,
                                      input_slots):
                    # Check whether an existing output variable could be passed
                    # to this input slot
                    ref = f'{info.name}:{slot.type}'
                    if ref not in output_variables:
                        # Perform a check through existing output variables to
                        # unhook input slot if it has been renamed
                        for key in existing_variable_keys:
                            variable = self.variable_registry[key]
                            if (index, info) in variable.input_slots:
                                variable.input_slots.remove((index, info))

                        # Store the reference to retain the Variable during
                        # cleanup
                        existing_variable_keys.append(ref)

                        # If another input slot has referenced this Variable,
                        # then simply add the data_source to the input_slots
                        # list, otherwise create a new Variable
                        if ref not in self.variable_registry.keys():
                            data = Variable(
                                type=slot.type,
                                layer=index,
                                name=info.name
                            )
                            self.variable_registry[ref] = data
                        else:
                            self.variable_registry[ref].input_slots.append(
                                (index, info)
                            )

                    # Search through existing variables to find a name and
                    # type match
                    else:
                        for variable in self.variable_registry.values():
                            name_check = variable.name == info.name
                            type_check = variable.type == slot.type
                            if name_check and type_check:
                                if (index, info) not in variable.input_slots:
                                    variable.input_slots.append(
                                        (index, info)
                                    )

        # Clean up any Variable that no longer have slots that exist
        # in the workflow
        non_existing_variables = [
            ref for ref in self.variable_registry.keys()
            if ref not in existing_variable_keys
        ]
        for key in non_existing_variables:
            self.variable_registry.pop(key, None)
