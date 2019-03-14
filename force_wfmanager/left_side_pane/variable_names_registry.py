import itertools
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
    #: representing the output variables produced by that execution layer
    exec_layer_output = List(Tuple(Identifier, CUBAType))

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
    available_variables_stack = List(exec_layer_output)

    # ----------
    # Properties
    # ----------

    #: A list of type lookup dictionaries, with one dictionary for each
    #: execution layer
    available_variables_by_type = Property(
        List(exec_layer_by_type), depends_on="available_variables_stack"
        )

    #: Same structure as available_variables_stack, but this contains
    #: the cumulated information. From the example above, this would contain::
    #:
    #:     [["Vol_A", "Vol_B"],
    #:      ["Vol_A", "Vol_B"],
    #:      ["Vol_A", "Vol_B", "Pressure_A"]]
    #:
    available_variables = Property(List(List(Identifier)),
                                   depends_on="available_variables_stack")

    #: Gives only the names of the variables that are produced by data sources.
    #: It does not include MCO parameters.
    data_source_outputs = Property(List(Identifier),
                                   depends_on="available_variables_stack")

    #: MCO Parameter names available to the workflow
    parameters = Property(List(Identifier),
                          depends_on="available_variables_stack")

    #: KPI names available to the workflow
    kpi_names = Property(List(Identifier), depends_on='workflow.mco.kpis.name')

    #: Both MCO Parameter and KPI names
    kpi_params = Property(List(Identifier), depends_on='parameters,kpi_names')

    def __init__(self, workflow, *args, **kwargs):
        super(VariableNamesRegistry, self).__init__(*args, **kwargs)
        self.workflow = workflow

    @on_trait_change(
        'workflow.mco.parameters.name,'
        'workflow.execution_layers.data_sources.output_slot_info.name,'
        'workflow.mco.parameters.type'
    )
    def update_available_variables_stack(self):
        """Updates the list of available variables. At present getting
        the datasource output slots requires creating the datasource by
        calling ``create_data_source()``."""
        # FIXME: Remove reliance on create_data_source(). If one datasource
        # FIXME: has an error, this shouldn't blow up the whole workflow.
        # FIXME: Especially during the setup phase!
        stack = []
        # At the first layer, the available variables are the MCO parameters
        if self.workflow.mco is None:
            stack.append([])
        else:
            stack.append([
                (p.name, p.type) for p in self.workflow.mco.parameters
                if len(p.name) != 0
            ])

        for layer in self.workflow.execution_layers:
            stack_entry_for_layer = []
            for ds_model in layer.data_sources:
                ds_names = [info.name for info in ds_model.output_slot_info]

                # This try-except is also in execute.py in force_bdss, so if
                # this fails the workflow would not be able to run anyway.
                try:
                    ds = ds_model.factory.create_data_source()
                    # ds.slots() returns (input_slots, output_slots)
                    ds_output_slots = ds.slots(ds_model)[1]
                except Exception:
                    log.exception(
                        "Unable to create data source from factory '{}' "
                        "in plugin '{}'. This may indicate a programming "
                        "error in the plugin".format(
                            ds_model.factory.id,
                            ds_model.factory.plugin.id))
                    raise

                ds_types = [slot.type for slot in ds_output_slots]

                stack_entry_for_layer.extend([
                    (ds_name, ds_type) for ds_name, ds_type
                    in zip(ds_names, ds_types) if ds_name != ''
                ])
            stack.append(stack_entry_for_layer)

        self.available_variables_stack = stack

    @cached_property
    def _get_available_variables(self):
        stack = self.available_variables_stack
        res = []
        for idx in range(len(stack)):
            cumsum = []
            for output_info in stack[0:idx + 1]:
                cumsum.extend([output[0] for output in output_info])
            res.append(cumsum)
        return res

    @cached_property
    def _get_data_source_outputs(self):
        stack = self.available_variables_stack
        res = []

        for output_info in stack[1:]:
            res.extend([output[0] for output in output_info])
        return res

    @cached_property
    def _get_parameters(self):
        stack = self.available_variables_stack

        res = [output[0] for output in stack[0]]
        return res

    @cached_property
    def _get_kpi_names(self):
        if self.workflow.mco:
            return [kpi.name for kpi in self.workflow.mco.kpis]
        else:
            return []

    @cached_property
    def _get_kpi_params(self):
        return [
            name for name in itertools.chain(self.kpi_names,self.parameters)
        ]

    @cached_property
    def _get_available_variables_by_type(self):
        stack = self.available_variables_stack
        res = []
        res_dict = {}

        for idx in range(len(stack)):
            for output_info in stack[idx]:
                var_name = output_info[0]
                var_type = output_info[1]
                if var_type in res_dict:
                    res_dict[var_type].append(var_name)
                else:
                    res_dict[var_type] = [var_name]
            res.append(res_dict)
        return res
