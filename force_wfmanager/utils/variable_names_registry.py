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
    output_slot = Instance(OutputSlotInfo)

    # DataSources where Variable is used as an input
    input_slots = List(Tuple(Int, InputSlotInfo))

    # ---------------------
    # Dependent Attributes
    # ---------------------

    # Name of Variable, listens to output_slot if updated by UI
    name = Identifier()

    # ------------------
    #     Properties
    # ------------------

    label = Property(Unicode, depends_on='output_slot.name,type')

    # ------------------
    #     Listeners
    # ------------------

    def _get_label(self):
        return f'{self.type} {self.name}'

    @on_trait_change('output_slot.name')
    def update_name(self):
        """If the origin output slot name is changed, update the
        variable name and all linked input slots"""

        self.name = self.output_slot.name

        for input_slot in self.input_slots:
            input_slot[1].name = self.name

    # ------------------
    #   Public Methods
    # ------------------

    def check_input_slot_hook(self, input_slot, type, index):
        """Check whether an input slot should be hooked up or removed from the
        Variable"""

        name_check = self.name == input_slot.name
        type_check = self.type == type

        # If the input slot name and type matches the Variablem, hooked it up
        if name_check and type_check:
            if (index, input_slot) not in self.input_slots:
                self.input_slots.append((index, input_slot))
            return True

        # Else remove it if it has been hooked up previously
        if (index, input_slot) in self.input_slots:
            self.input_slots.remove((index, input_slot))
            return False

    def verify(self):
        """Reports a validation warning if variable is used as
        an input before being generated
        """
        errors = []

        # Only perform check if Variable is being created by a
        # DataSource and has a defined name
        if self.output_slot is not None:
            for layer, slot in self.input_slots:
                if layer <= self.layer:
                    errors.append(
                        VerifierError(
                            subject=slot,
                            local_error=('Variable is being used as an '
                                         'input before being generated as'
                                         ' an output'),
                            global_error=('A variable is being used as an '
                                          'input before being generated as'
                                          ' an output')
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
    _variable_registry = Dict(Unicode, Dict(Unicode, Variable))

    # -------------
    #   Properties
    # -------------

    #: A list containing the values of variable_registry dictionary
    available_variables = Property(
        List(Variable),
        depends_on='_variable_registry'
    )

    #: A list containing a reference to each variable available_variables
    variable_refs = Property(
        List(Unicode),
        depends_on='available_variables.[name,type]')

    #: Same structure as available_output_variables_stack, but this contains
    #: the cumulated information.
    available_variable_names = Property(
        List(List(Identifier)),
        depends_on="available_variables"
    )

    #: A list of type lookup dictionaries, with one dictionary for each
    #: execution layer
    available_variables_by_type = Property(
        List(exec_layer_by_type),
        depends_on="available_variables"
        )

    def __init__(self, workflow, *args, **kwargs):
        super(VariableNamesRegistry, self).__init__(*args, **kwargs)
        self.workflow = workflow

    def __variable_registry_default(self):
        """Default value for _variable_registry dictionary: split into two inner
        dictionaries, holding defined (created by a DataSource output slot
        and undefined (requiring to be created by a MCOParameter) Variables"""
        return {'defined': {},
                'undefined': {}}

    # ---------------
    #    Listeners
    # ---------------

    @cached_property
    def _get_available_variables(self):
        """Returns a list containing the values of _variable_registry"""

        available_variables = list(
            self._variable_registry['defined'].values()
        )
        available_variables += list(
            self._variable_registry['undefined'].values()
        )

        return available_variables

    @cached_property
    def _get_variable_refs(self):
        """Returns a list containing a reference to the names and type of
        each variable in available_variables"""

        variable_refs = [
            f'{variable.name}:{variable.type}'
            for variable in self.available_variables
        ]

        return variable_refs

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
            if variable.output_slot is None:
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
        used for persistence checking and cleanup purposes"""

        # Create references to the defined and undefined variable
        # registries (purely for flake8 ease due to long names)
        defined_registry = self._variable_registry['defined']
        undefined_registry = self._variable_registry['undefined']

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
                    # Key is a direct reference an output slot on
                    # data_source_model. Therefore it is unique and exists
                    # as long as the slot exists
                    key = f'{id(info)}'

                    # If slot is unnamed, continue and do not register it as
                    # a Variable. If the output slot has existed as a named
                    # Variable before, remove it from the registry
                    if info.name == '':
                        if key in defined_registry:
                            defined_registry.pop(key, None)
                        continue

                    # Only create a new Variable if it has not been defined
                    # from an output slot before this update
                    if key not in defined_registry:
                        data = Variable(
                            type=slot.type,
                            layer=index,
                            output_slot=info,
                        )
                        defined_registry[key] = data

                for info, slot in zip(data_source_model.input_slot_info,
                                      input_slots):

                    # Reference to the variable that an input slot on
                    # data_source_model points to. Multiple input slots
                    # can refer to the same output slot, so they do not
                    # possess a unique reference
                    key = f'{info.name}:{slot.type}'

                    # Check whether input slot can be hooked up to a
                    # existing Variable defined by an output slot
                    hooked_up = False
                    for variable in defined_registry.values():
                        hooked_up = (
                                hooked_up or variable.check_input_slot_hook(
                                    info, slot.type, index)
                        )

                    if not hooked_up:
                        # If not hooked up to an output slot, check whether
                        # input slot can be assigned to an existing undefined
                        # Variable. This will also remove the slot from any
                        # Variable if it is unnamed
                        for variable in undefined_registry.values():
                            variable.check_input_slot_hook(
                                info, slot.type, index)

                        # If slot is unnamed, continue and do not register it
                        # as a new Variable.
                        if info.name == '':
                            continue

                        if key not in undefined_registry:
                            # If no existing Variable could refer to input
                            # slot, create a new one
                            data = Variable(
                                type=slot.type,
                                layer=index,
                                name=info.name,
                                input_slots=[(index, info)]
                            )
                            undefined_registry[key] = data

                    else:
                        # If hooked up to an output slot, remove input slot
                        # from any undefined Variable
                        for variable in undefined_registry.values():
                            if (index, info) in variable.input_slots:
                                variable.input_slots.remove((index, info))

        # Clean up any Variables that no longer refer to any output or input
        # slots that exist in the workflow
        non_existing_variables = [
            key for key, variable in undefined_registry.items()
            if len(variable.input_slots) == 0
        ]
        for key in non_existing_variables:
            undefined_registry.pop(key, None)

    def verify(self):
        """Check all Variable output slots have a unique name / type and
        report any errors raised by each Variable"""

        errors = []

        for index, value in enumerate(self.variable_refs):
            if self.variable_refs.count(value) > 1:
                variable = self.available_variables[index]
                errors.append(
                   VerifierError(
                       subject=variable.output_slot,
                       local_error=('Output slot does not have a unique name'
                                    ' / type combination'),
                       global_error=('Two or more output slots share the same '
                                     'name / type combination')
                   )
                )

        for variable in self.available_variables:
            errors += variable.verify()

        return errors
