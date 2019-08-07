import logging

from traits.api import (
    HasStrictTraits, List, Instance, on_trait_change, Property,
    cached_property, Dict, Tuple, Unicode, Event)

from force_bdss.api import (
    Identifier, VerifierError
)
from force_bdss.local_traits import CUBAType

from force_wfmanager.ui.setup.process.process_view import ProcessView
from force_wfmanager.utils.variable import Variable

log = logging.getLogger(__name__)


class VariableNamesRegistry(HasStrictTraits):
    """ Class used for listening to the structure of the Workflow in
    order to check the available variables that can be used as input_slot_rows
    for each layer
    """

    # -------------------
    # Required Attributes
    # -------------------

    #: Process view for execution layer and data source views
    process_view = Instance(ProcessView, allow_none=False)

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
    _variable_registry = Dict(Unicode, Dict(Tuple, Variable))

    #: A list containing the values of variable_registry dictionary
    available_variables = List(Variable)

    verify_workflow_event = Event()

    # -------------
    #   Properties
    # -------------

    #: A list containing a reference to each variable available_variables
    variable_refs = Property(
        List(Tuple),
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
    def _get_variable_refs(self):
        """Returns a list containing a reference to the names and type of
        each variable in available_variables"""
        variable_refs = [
            (variable.name, variable.type)
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
        n_layers = len(self.process_view.execution_layer_views)
        available_variables = [
            [] for _ in range(n_layers+1)
        ]

        for variable in self.available_variables:
            # Fill the layers at which any output variable is accessible
            # by other DataSources
            if variable.origin is None:
                layer = 0
            else:
                layer = variable.layer_index + 1

            for index in range(layer, n_layers+1):
                if variable.name not in available_variables[index]:
                    available_variables[index].append(variable.name)

            # Fill the layers at which any input variable has been declared
            # and therefore needs to be generated by either an output slot
            # or MCO parameter
            for slot in variable.input_slot_rows:
                if slot[1].model.name not in available_variables[slot[0]]:
                    available_variables[slot[0]].append(slot[1].model.name)

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
        n_layers = len(self.process_view.execution_layer_views)
        available_variables = [
            {} for _ in range(n_layers+1)
        ]

        for variable in self.available_variables:
            # Reserve the first list for variables from the MCO
            if variable.origin is None:
                layer = 0
            else:
                layer = variable.layer_index + 1

            var_dict = available_variables[layer]

            if variable.type in var_dict:
                var_dict[variable.type].append(variable)
            else:
                var_dict[variable.type] = [variable]

        return available_variables

    @on_trait_change(
        'process_view.execution_layer_views.data_source_views.'
        'verify_workflow_event'
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

        # Tracks keys that refer to currently existing slots -
        # used to clean up Variables later
        existing_keys = []

        for layer in self.process_view.execution_layer_views:
            for data_source_view in layer.data_source_views:

                for info_slot in data_source_view.output_slots_representation:
                    # Key is a direct reference an output slot on
                    # data_source_model. Therefore it is unique and exists
                    # as long as the slot exists
                    key = (str(id(info_slot)),)
                    # If slot is unnamed, continue and do not register it as
                    # a Variable. If the output slot has existed as a named
                    # Variable before, continue so as it will be later removed
                    # from the registry
                    if info_slot.model.name == '':
                        continue

                    # Only create a new Variable if it has not been defined
                    # from an output slot before this update
                    if key not in defined_registry:
                        data = Variable(
                            origin=data_source_view,
                            layer_index=layer.layer_index,
                            output_slot_row=info_slot,
                        )
                        defined_registry[key] = data
                    existing_keys.append(key)

                for info_slot in data_source_view.input_slots_representation:

                    # Reference to the variable that an input slot on
                    # data_source_model points to. Multiple input slots
                    # can refer to the same output slot, so they do not
                    # possess a unique reference
                    key = (info_slot.model.name, info_slot.type)
                    input_slot = (layer.layer_index, info_slot)
                    # Check whether input slot can be hooked up to a
                    # existing Variable defined by an output slot
                    hooked_up = False
                    for variable in defined_registry.values():
                        hooked_up = (
                            hooked_up or variable.check_input_slot_hook(
                                *input_slot
                            )
                        )

                    if not hooked_up:
                        # If not hooked up to an output slot, check whether
                        # input slot can be assigned to an existing undefined
                        # Variable. This will also remove the slot from any
                        # Variable if it is unnamed
                        for variable in undefined_registry.values():
                            variable.check_input_slot_hook(
                                *input_slot
                            )

                        # If slot is unnamed, continue and do not register it
                        # as a new Variable.
                        if info_slot.model.name == '':
                            continue

                        if key not in undefined_registry:
                            # If no existing Variable could refer to input
                            # slot, create a new one
                            data = Variable(
                                type=info_slot.type,
                                name=info_slot.model.name,
                                input_slot_rows=[input_slot]
                            )
                            undefined_registry[key] = data

                    else:
                        # If hooked up to an output slot, remove input slot
                        # from any undefined Variable
                        for variable in undefined_registry.values():
                            if input_slot in variable.input_slot_rows:
                                variable.input_slots.remove(input_slot)

        # Clean up any Variables that no longer refer to any output or input
        # slots that exist in the workflow
        empty_defined_variables = [
            key for key, variable in defined_registry.items()
            if variable.empty
        ]
        empty_defined_variables += [
            key for key in defined_registry.keys()
            if key not in existing_keys and key not in empty_defined_variables
        ]
        for key in empty_defined_variables:
            defined_registry.pop(key, None)

        empty_undefined_variables = [
            key for key, variable in undefined_registry.items()
            if variable.empty
        ]
        for key in empty_undefined_variables:
            undefined_registry.pop(key, None)

        self.update_available_variables()

    # ------------------
    #   Public Methods
    # ------------------

    def update_available_variables(self):
        """Updates a list containing the values of _variable_registry"""
        available_variables = list(
            self._variable_registry['defined'].values()
        )
        available_variables += list(
            self._variable_registry['undefined'].values()
        )
        self.available_variables = available_variables
        self.verify_workflow_event = True

    def verify(self):
        """Check all Variable output slots have a unique name / type and
        report any errors raised by each Variable"""

        errors = []

        for index, value in enumerate(self.variable_refs):
            if self.variable_refs.count(value) > 1:
                variable = self.available_variables[index]
                errors.append(
                   VerifierError(
                       subject=variable.output_slot_info,
                       local_error=('Output slot does not have a unique name'
                                    ' / type combination'),
                       global_error=('Two or more output slots share the same '
                                     'name / type combination')
                   )
                )

        for variable in self.available_variables:
            errors += variable.verify()

        return errors
