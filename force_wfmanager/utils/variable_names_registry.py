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

    #: Dictionary allowing the lookup of Variable objects with an associated
    #: key. Practically, these keys are only used by update__variable_registry
    #: to maintain the dictionary whenever its content is edited. Therefore
    #: the dictionary itself remains private, whilst the Variables within the
    #: dictionary are referred to externally, using the properties
    #: available_variables, available_variable_names and
    #: available_variables_by_type
    _variable_registry = Dict(Unicode, Variable)

    # -------------
    #   Properties
    # -------------

    #: A list containing the values of variable_registry dictionary
    available_variables = Property(
        List(Variable),
        depends_on='_variable_registry'
    )

    #: Same structure as available_output_variables_stack, but this contains
    #: the cumulated information.
    available_variable_names = Property(
        List(List(Identifier)),
        depends_on="_variable_registry"
    )

    #: A list of type lookup dictionaries, with one dictionary for each
    #: execution layer
    available_variables_by_type = Property(
        List(exec_layer_by_type),
        depends_on="_variable_registry"
        )

    def __init__(self, workflow, *args, **kwargs):
        super(VariableNamesRegistry, self).__init__(*args, **kwargs)
        self.workflow = workflow

    # ---------------
    #    Listeners
    # ---------------

    @cached_property
    def _get_available_variables(self):
        """Returns a list containing the values of _variable_registry"""
        available_variables = list(self._variable_registry.values())

        return available_variables

    @cached_property
    def _get_available_variable_names(self):
        """Returns a cumulative list of variable names, indicating the layers
        at which they are available
        The first entry is a list of all the variables that are visible at the
        first layer, i.e. those which need to come from the MCO. The second
        entry also contains all the variable names that the first layer added.
        From the example above, the structure,

           [["Vol_A", "Vol_B"],
            ["Vol_A", "Vol_B", "Pressure_A"],
            ["Vol_A", "Vol_B", "Pressure_A", "Pressure_B"]]

        means:
        - the first layer has "Vol_A" and "Vol_B" available.
        - the second layer has "Pressure_A", "Vol_A" and "Vol_B" available,
          indicating that the first layer added "Pressure_A"
        - the last layer has "Pressure_A", "Pressure_B, ""Vol_A" and "Vol_B"
          available, indicating that the second layer added "Pressure_B"

        The size of the base list should equal to the number of layers plus
        one, with the last layer containing all the variables created by all
        execution layers.
        """
        n_layers = len(self.workflow.execution_layers)
        available_variables = [
            [] for _ in range(n_layers+1)
        ]

        for variable in self.available_variables:
            # Fill the layers at which any output variable is accessible
            # by other DataSources
            for index in range(variable.layer+1, n_layers+1):
                if variable.name not in available_variables[index]:
                    available_variables[index].append(variable.name)

            # Fill the layers at which any input variable has been declared
            # and therefore needs to be generated
            for slot in variable.input_slots:
                if slot[1].name not in available_variables[slot[0]]:
                    available_variables[slot[0]].append(slot[1].name)

        return available_variables

    def _get_available_variables_by_type(self):
        """Returns a list of dictionaries, referring to the variables created
        in each execution layer. The key for each dictionary indicates the
        variable CUBA type.
        From the example above, the structure,

           [{"VOLUME": [<Variable object>, <Variable object>]}
            {"PRESSURE": [<Variable object>]},
            {"PRESSURE": [<Variable object>]}]

        means:
        - two variables of type "PRESSURE" are required as MCO Parameters.
        - the first layer added a variable of type "PRESSURE".
        - the second layer added a variable of type "PRESSURE".
        """
        n_layers = len(self.workflow.execution_layers)
        available_variables = [
            {} for _ in range(n_layers+1)
        ]

        for variable in self.available_variables:
            # Reserve the first list for variables from the MCO
            if variable.origin is None:
                layer = 0
            else:
                layer = variable.layer + 1

            var_dict = available_variables[layer]

            if variable.type in var_dict:
                var_dict[variable.type].append(variable)
            else:
                var_dict[variable.type] = [variable]

        return available_variables

    @on_trait_change(
        'workflow.execution_layers.data_sources.'
        '[input_slot_info.name,output_slot_info.name]'
    )
    def update__variable_registry(self):
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
                    if key not in self._variable_registry.keys():
                        data = Variable(
                            type=slot.type,
                            layer=index,
                            origin_slot=info,
                            origin=data_source_model
                        )
                        self._variable_registry[key] = data

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
                            variable = self._variable_registry[key]
                            if (index, info) in variable.input_slots:
                                variable.input_slots.remove((index, info))

                        # Store the reference to retain the Variable during
                        # cleanup
                        existing_variable_keys.append(ref)

                        # If another input slot has referenced this Variable,
                        # then simply add the data_source to the input_slots
                        # list, otherwise create a new Variable
                        if ref not in self._variable_registry.keys():
                            data = Variable(
                                type=slot.type,
                                layer=index,
                                name=info.name
                            )
                            self._variable_registry[ref] = data
                        else:
                            self._variable_registry[ref].input_slots.append(
                                (index, info)
                            )

                    # Search through existing variables to find a name and
                    # type match
                    else:
                        for variable in self._variable_registry.values():
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
            ref for ref in self._variable_registry.keys()
            if ref not in existing_variable_keys
        ]
        for key in non_existing_variables:
            self._variable_registry.pop(key, None)
