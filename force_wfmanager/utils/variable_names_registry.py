import logging

from traits.api import (
    HasStrictTraits, List, Instance, on_trait_change, Property,
    cached_property, Dict, Tuple)

from force_bdss.api import Identifier, Workflow
from force_bdss.local_traits import CUBAType

log = logging.getLogger(__name__)


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
    data_source_input = List(Tuple(Identifier, CUBAType))

    #: For each execution layer, there will be a list of (name, type) pairs
    #: representing the output variables produced by that execution layer
    data_source_output = List(Tuple(Identifier, CUBAType))

    #: For each execution layer, there will be a list of (name, type) pairs
    #: representing the input variables produced by that execution layer
    exec_layer_input = List(data_source_input)

    #: For each execution layer, there will be a list of (name, type) pairs
    #: representing the output variables produced by that execution layer
    exec_layer_output = List(data_source_output)

    #: Dictionary allowing the lookup of names associated with a chosen CUBA
    #: type.
    exec_layer_by_type = Dict(CUBAType, List(Identifier))

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

        for input_layer, output_layer in zip(input_stack, output_stack):
            layer_variables = []
            generator = zip(input_layer, output_layer)
            for input_data_source, output_data_source in generator:
                layer_variables += [
                    variable[0] for variable in input_data_source
                ]
                layer_variables += [
                    variable[0] for variable in output_data_source
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
            generator = zip(input_layer, output_layer)
            for input_data_source, output_data_source in generator:
                for input_info in input_data_source:
                    var_name = input_info[0]
                    var_type = input_info[1]

                    if var_type in res_dict:
                        res_dict[var_type].append(var_name)
                    else:
                        res_dict[var_type] = [var_name]

                for output_info in output_data_source:
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
            for info in layer:
                res.extend([value[0] for value in info
                            if value[0] not in res])
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

                input_stack_entry_for_layer.append([
                    (name, type) for name, type
                    in zip(input_names, input_types) if name != ''
                ])
                output_stack_entry_for_layer.append([
                    (name, type) for name, type
                    in zip(output_names, output_types) if name != ''
                ])

            input_stack.append(input_stack_entry_for_layer)
            output_stack.append(output_stack_entry_for_layer)

        self.available_input_variables_stack = input_stack
        self.available_output_variables_stack = output_stack
