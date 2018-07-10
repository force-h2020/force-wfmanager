from traits.api import (
    HasStrictTraits, List, Instance, on_trait_change, Property,
    cached_property, Dict)

from force_bdss.api import Identifier, Workflow
from force_bdss.local_traits import CUBAType


class VariableNamesRegistry(HasStrictTraits):
    """ Class used for listening to the structure of the Workflow in order to
    check the available variables that can be used as inputs for each layer
    """
    #: Workflow model
    workflow = Instance(Workflow, allow_none=False)

    #: List of lists of the available variables. This is not a cumulative list.
    #: The first entry is a list of all the variables that are visible at the
    #: first layer.
    #: The second entry is a list of all the variable names that the first
    #: layer added. NOT all the variables.
    #: For example, a situation like::
    #:
    #:     [[{'name': "pikachu", 'type': "electric"},
    #:       {'name': "squirtle", 'type': "water"],
    #:     [],
    #      [{'name': "scyther", 'type': "bug"}]]
    #:
    #: means:
    #: - the first layer has available "pikachu" and "squirtle".
    #: - the second layer has available "pikachu" and "squirtle",
    #: because the first layer added nothing (hence the empty second list)
    #: - the third layer has available "pikachu", "squirtle" and "scyther".
    #:
    #: The size of the base list should be the number of layers plus one.
    #: the last one being the variables that are added by the last layer.

    available_variables_stack = List(List(Dict(Identifier, CUBAType)))

    #: Same structure as available_variables_stack, but this contains
    #: the cumulated information. From the example above, this would contain::
    #:
    #:     [["pikachu", "squirtle"],
    #:      ["pikachu", "squirtle"],
    #:      ["pikachu", "squirtle", "scyther"]]
    #:
    available_variables = Property(List(List(Identifier)),
                                   depends_on="available_variables_stack")

    #: Gives only the names of the variables that are produced by data sources.
    #: It does not include MCO parameters.
    data_source_outputs = Property(List(Identifier),
                                   depends_on="available_variables_stack")

    def __init__(self, workflow, *args, **kwargs):
        super(VariableNamesRegistry, self).__init__(*args, **kwargs)
        self.workflow = workflow

    @on_trait_change(
        'workflow.mco.parameters.name,'
        'workflow.execution_layers.data_sources.output_slot_info.name,'
        'workflow.mco.parameters.type,'
    )
    def update_available_variables_stack(self):
        stack = []

        # At the first layer, the available variables are the MCO parameters
        if self.workflow.mco is None:
            stack.append([])
        else:
            stack.append([{'name': p.name, 'type': p.type}
                         for p in self.workflow.mco.parameters
                         if len(p.name) != 0
                          ])

        for layer in self.workflow.execution_layers:
            stack_entry_for_layer = []
            for ds in layer.data_sources:
                ds_names = [info.name for info in ds.output_slot_info]
                ds_output_slots = ds.factory.create_data_source().slots(ds)[1]
                ds_types = [slot.type for slot in ds_output_slots]

                stack_entry_for_layer.extend(
                    [{'name': ds_name, 'type': ds_type}
                     for ds_name, ds_type in zip(ds_names, ds_types)
                     if ds_name != ''])
            stack.append(stack_entry_for_layer)

        self.available_variables_stack = stack

    @cached_property
    def _get_available_variables(self):
        stack_dicts = self.available_variables_stack
        res = []

        for idx in range(len(stack_dicts)):
            cumsum = []
            for output_info in stack_dicts[0:idx + 1]:
                cumsum.extend([out_dict['name'] for out_dict in output_info])
            res.append(cumsum)

        return res

    @cached_property
    def _get_data_source_outputs(self):
        stack_dicts = self.available_variables_stack
        res = []

        for output_info in stack_dicts[1:]:
            res.extend([out_dict['name'] for out_dict in output_info])

        return res

    def available_variables_by_type(self, variable_type):
        stack_dicts = self.available_variables_stack
        res = []

        for idx in range(len(stack_dicts)):
            cumsum = []
            for output_info in stack_dicts[0:idx + 1]:
                cumsum.extend([out_dict['name'] for out_dict in output_info
                               if out_dict['type'] == variable_type])
            res.append(cumsum)

        return res
