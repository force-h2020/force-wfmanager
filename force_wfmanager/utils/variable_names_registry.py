import logging

from traits.api import (
    HasStrictTraits, List, Instance, on_trait_change, Property,
    cached_property, Dict, Tuple, HasTraits, Int, Unicode)

from force_bdss.api import (
    Identifier, Workflow, BaseDataSourceModel, InputSlotInfo
)
from force_bdss.local_traits import CUBAType

log = logging.getLogger(__name__)


class Variable(HasTraits):

    name = Identifier()

    type = CUBAType()

    layer = Int()

    origin = Instance(BaseDataSourceModel)

    inputs = List(BaseDataSourceModel)

    label = Property(Unicode, depends_on='name,type')

    def _get_label(self):
        return f'{self.type} {self.name}'



class VariableNamesRegistry(HasStrictTraits):
    """ Class used for listening to the structure of the Workflow in order to
    check the available variables that can be used as inputs for each layer
    """

    # -------------------
    # Required Attributes
    # -------------------

    #: Workflow model
    workflow = Instance(Workflow, allow_none=False)

    # ------------------
    # Regular Attributes
    # ------------------

    #: For each execution layer, there will be a list of (name, type) pairs
    #: representing the input variables produced by that execution layer
    data_source_input = Tuple(Identifier, CUBAType)

    #: For each execution layer, there will be a list of (name, type) pairs
    #: representing the output variables produced by that execution layer
    data_source_output = Tuple(Identifier, CUBAType)

    #: For each execution layer, there will be a list of (name, type) pairs
    #: representing the input variables produced by that execution layer
    exec_layer_input = List(data_source_input)

    #: For each execution layer, there will be a list of (name, type) pairs
    #: representing the output variables produced by that execution layer
    exec_layer_output = List(data_source_output)

    #: Dictionary allowing the lookup of names associated with a chosen CUBA
    #: type.
    exec_layer_by_type = Dict(CUBAType, List(Identifier))

    variable_database = Dict(Unicode, Variable)

    # ------------------
    # Derived Attributes
    # ------------------

    #: List of lists of the available variables.
    #: The first entry is a list of all the variables that are visible at the
    #: first layer, i.e. those which come from the MCO.
    #: The second entry is a list of all the variable names that the first
    #: layer added. NOT all the variables.
    #: For example, a situation like::
    #:
    #:     [[("Vol_A", "Volume"), ("Vol_B", "Volume")], [],
    #      [("Pressure_A", "Pressure")]]
    #:
    #: means:
    #: - the first layer has "Vol_A" and "Vol_B" available.
    #: - the second layer has "Vol_A" and "Vol_B" available,
    #: because the first layer added nothing (hence the empty second list)
    #: - the third layer has "Vol_A", "Vol_B" and "Pressure_A" available.
    #:
    #: The size of the base list should be the number of layers plus one.
    #: the last one being the variables that are added by the last layer.
    #:
    #: Listens to: `workflow.mco.parameters.name`,
    #: `workflow.execution_layers.data_sources.output_slot_info.name`,
    #: `workflow.mco.parameters.type`
    available_input_variables_stack = List(exec_layer_input)

    available_output_variables_stack = List(exec_layer_output)

    # -------------
    #   Properties
    # -------------

    #: A list of type lookup dictionaries, with one dictionary for each
    #: execution layer
    available_variables_by_type = Property(
        List(exec_layer_by_type),
        depends_on="available_output_variables_stack,"
                   "available_input_variables_stack"
        )

    #: Same structure as available_output_variables_stack, but this contains
    #: the cumulated information. From the example above, this would contain::
    #:
    #:     [["Vol_A", "Vol_B"],
    #:      ["Vol_A", "Vol_B"],
    #:      ["Vol_A", "Vol_B", "Pressure_A"]]
    #:
    available_variables = Property(
        List(List(Identifier)),
        depends_on="available_output_variables_stack,"
                   "available_input_variables_stack"
    )

    #: Gives only the names of the variables that are produced by data sources.
    #: It does not include MCO parameters.
    data_source_outputs = Property(
        List(Identifier), depends_on="available_output_variables_stack"
    )
    data_source_inputs = Property(
        List(Identifier), depends_on="available_input_variables_stack"
    )

    def __init__(self, workflow, *args, **kwargs):
        super(VariableNamesRegistry, self).__init__(*args, **kwargs)
        self.workflow = workflow

    # ---------------
    #    Listeners
    # ---------------

    @cached_property
    def _get_available_variables(self):
        output_stack = self.available_output_variables_stack
        input_stack = self.available_input_variables_stack
        variables = []

        parameter_names = []
        if self.workflow.mco is not None:
            for parameter in self.workflow.mco.parameters:
                parameter_names = []
                parameter_names.append(parameter.name)

        variables.append(parameter_names)

        for input_layer, output_layer in zip(input_stack, output_stack):
            layer_variables = []
            layer_variables += [
                variable[0] for variable in input_layer
            ]
            layer_variables += [
                variable[0] for variable in output_layer
            ]
            variables.append(layer_variables)

        return variables

    @cached_property
    def _get_data_source_outputs(self):
        stack = self.available_output_variables_stack
        return self._get_data_source_names(stack)

    @cached_property
    def _get_data_source_inputs(self):
        stack = self.available_input_variables_stack
        return self._get_data_source_names(stack)

    @cached_property
    def _get_available_variables_by_type(self):
        output_stack = self.available_output_variables_stack
        input_stack = self.available_input_variables_stack
        res = []

        for input_layer, output_layer in zip(input_stack, output_stack):
            res_dict = {}
            for input_info in input_layer:
                var_name = input_info[0]
                var_type = input_info[1]

                if var_type in res_dict:
                    res_dict[var_type].append(var_name)
                else:
                    res_dict[var_type] = [var_name]

            for output_info in output_layer:
                var_name = output_info[0]
                var_type = output_info[1]

                if var_type in res_dict:
                    res_dict[var_type].append(var_name)
                else:
                    res_dict[var_type] = [var_name]

            res.append(res_dict)
        return res

    def _get_data_source_names(self, stack):
        res = []
        for layer in stack:
            res.extend([value for value in layer
                        if value not in res])
        return res

    @on_trait_change(
        'workflow.mco.parameters.[name,type],'
        'workflow.execution_layers.data_sources.'
        '[input_slot_info.name,output_slot_info.name]'
    )
    def update_available_variables_stacks(self):
        """Updates the list of available variables. At present getting
        the datasource output slots requires creating the datasource by
        calling ``create_data_source()``."""
        # FIXME: Remove reliance on create_data_source(). If one datasource
        # FIXME: has an error, this shouldn't blow up the whole workflow.
        # FIXME: Especially during the setup phase!
        input_stack = []
        output_stack = []
        # At the first layer, the available variables are the MCO parameters

        for layer in self.workflow.execution_layers:
            input_stack_entry_for_layer = []
            output_stack_entry_for_layer = []

            for data_source_model in layer.data_sources:
                input_names = [
                    info.name for info in data_source_model.input_slot_info
                ]
                output_names = [
                    info.name for info in data_source_model.output_slot_info
                ]

                # This try-except is also in execute.py in force_bdss, so if
                # this fails the workflow would not be able to run anyway.
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

                input_types = [slot.type for slot in input_slots]
                output_types = [slot.type for slot in output_slots]

                input_stack_entry_for_layer.extend([
                    (name, type) for name, type
                    in zip(input_names, input_types) if name != ''
                ])
                output_stack_entry_for_layer.extend([
                    (name, type) for name, type
                    in zip(output_names, output_types) if name != ''
                ])

            input_stack.append(input_stack_entry_for_layer)
            output_stack.append(output_stack_entry_for_layer)

        self.available_input_variables_stack = input_stack
        self.available_output_variables_stack = output_stack

    @on_trait_change(
        'workflow.execution_layers.data_sources.'
        '[input_slot_info.name,output_slot_info.name]'
    )
    def update_variable_database(self):

        # List of keys referring to existing variables
        existing_variable_keys = []

        # List of references to variables with a defined origin
        output_variables = []

        for index, layer in enumerate(self.workflow.execution_layers):
            for data_source_model in layer.data_sources:
                # This try-except is also in execute.py in force_bdss, so if
                # this fails the workflow would not be able to run anyway.
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

                for info, slot in zip(data_source_model.output_slot_info, output_slots):
                    # Key is reference to slot attribute on data_source_model. Therefore it
                    # is unique and exists as long as the slot exists
                    key = f'{id(info)}'
                    existing_variable_keys.append(key)

                    # If the Variable has been defined before this update, do not
                    # create it again
                    if key not in self.variable_database.keys():
                        data = Variable(
                            layer=index,
                            origin=data_source_model
                        )
                        self.variable_database[key] = data

                    # Update Variable object attributes with UI slots
                    self.variable_database[key].name = info.name
                    self.variable_database[key].type = slot.type

                    # Store a reference to the existing name and type of the Variable -
                    # this is used to cross check against possible input slots
                    ref = f'{info.name}:{slot.type}'
                    if ref not in output_variables:
                        output_variables.append(ref)

                for info, slot in zip(data_source_model.input_slot_info, input_slots):
                    # Check whether an existing output variable could be passed to this
                    # input slot
                    ref = f'{info.name}:{slot.type}'
                    if ref not in output_variables:
                        # Store the reference to retain the Variable during cleanup
                        existing_variable_keys.append(ref)

                        # If another input slot has referenced this Variable, then simply
                        # add the data_source to the input_list, otherwise create a new
                        # Variable
                        if ref not in self.variable_database.keys():
                            data = Variable(
                                name=info.name,
                                type=slot.type,
                                layer=index
                            )
                            self.variable_database[ref] = data
                        else:
                            self.variable_database[ref].inputs.append(data_source_model)

                    # Search through existing variables to find a name and type match
                    else:
                        for variable in self.variable_database.values():
                            if variable.name == info.name and variable.type == slot.type:
                                variable.inputs.append(data_source_model)

        # Clean up any Variable that no longer have slots that exist in the workflow
        non_existing_variables = [ref for ref in self.variable_database.keys()
                                  if ref not in existing_variable_keys]
        for key in non_existing_variables:
            self.variable_database.pop(key, None)
