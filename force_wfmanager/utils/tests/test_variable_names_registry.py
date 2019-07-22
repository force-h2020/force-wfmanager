import unittest

from force_bdss.api import OutputSlotInfo, InputSlotInfo, ExecutionLayer
from force_bdss.core.workflow import Workflow
from force_bdss.tests.probe_classes.data_source import (
    ProbeDataSourceFactory
)
from force_bdss.tests.probe_classes.mco import (
    ProbeParameterFactory, ProbeMCOFactory
)
from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin

from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry)


def get_basic_variable_names_registry():
    plugin = ProbeExtensionPlugin()
    workflow = Workflow()

    mco_factory = ProbeMCOFactory(plugin)
    mco = mco_factory.create_model()

    param_factory = ProbeParameterFactory(mco_factory)
    param1 = param_factory.create_model()
    param2 = param_factory.create_model()
    param3 = param_factory.create_model()

    data_source_factory = ProbeDataSourceFactory(
        plugin,
        input_slots_size=1,
        output_slots_size=1)
    # first layer
    data_source1 = data_source_factory.create_model()
    data_source2 = data_source_factory.create_model()

    # second layer
    data_source3 = data_source_factory.create_model()

    # third layer
    data_source4 = data_source_factory.create_model()

    workflow.mco = mco
    mco.parameters = [param1, param2, param3]
    workflow.execution_layers.extend([
        ExecutionLayer(
            data_sources=[data_source1, data_source2]
        ),
        ExecutionLayer(
            data_sources=[data_source3]
        ),
        ExecutionLayer(
            data_sources=[data_source4]
        )
    ]
    )

    return VariableNamesRegistry(workflow=workflow)


class VariableNamesRegistryTest(unittest.TestCase):
    def setUp(self):
        self.registry = get_basic_variable_names_registry()
        self.workflow = self.registry.workflow
        self.param1 = self.workflow.mco.parameters[0]
        self.param2 = self.workflow.mco.parameters[1]
        self.param3 = self.workflow.mco.parameters[2]
        self.data_source1 = self.workflow.execution_layers[0].data_sources[0]
        self.data_source2 = self.workflow.execution_layers[0].data_sources[1]
        self.data_source3 = self.workflow.execution_layers[1].data_sources[0]
        self.data_source4 = self.workflow.execution_layers[2].data_sources[0]

    def test_registry_init(self):
        self.assertEqual(
            3, len(self.registry.available_input_variables_stack)
        )
        self.assertEqual(
            3, len(self.registry.available_output_variables_stack)
        )

    def test_variables_stacks(self):

        self.data_source1.input_slot_info = [InputSlotInfo(name='V1')]
        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]

        self.assertEqual([[('V1', 'PRESSURE')], []],
                         self.registry.available_input_variables_stack[0])
        self.assertEqual([[('T1', 'PRESSURE')], []],
                         self.registry.available_output_variables_stack[0])

        self.data_source2.input_slot_info = [InputSlotInfo(name='V2')]
        self.data_source2.output_slot_info = [OutputSlotInfo(name='T2')]

        self.assertEqual([[('V1', 'PRESSURE')], [('V2', 'PRESSURE')]],
                         self.registry.available_input_variables_stack[0])
        self.assertEqual([[('T1', 'PRESSURE')], [('T2', 'PRESSURE')]],
                         self.registry.available_output_variables_stack[0])

        self.data_source3.input_slot_info = [InputSlotInfo(name='T1')]
        self.data_source3.output_slot_info = [OutputSlotInfo(name='T3')]
        self.assertEqual([[('T1', 'PRESSURE')]],
                         self.registry.available_input_variables_stack[1])
        self.assertEqual([[('T3', 'PRESSURE')]],
                         self.registry.available_output_variables_stack[1])

        self.data_source3.input_slot_info = [InputSlotInfo(name='')]
        self.data_source3.changes_slots = True
        self.data_source3.output_slot_info = [OutputSlotInfo(name='T3')]
        self.assertEqual([[]],
                         self.registry.available_input_variables_stack[1])

    def test_available_variables(self):

        self.data_source1.input_slot_info = [InputSlotInfo(name='V1')]
        self.data_source2.input_slot_info = [InputSlotInfo(name='V2')]
        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        self.data_source2.output_slot_info = [OutputSlotInfo(name='T2')]

        self.data_source3.input_slot_info = [InputSlotInfo(name='T1')]
        self.data_source3.output_slot_info = [OutputSlotInfo(name='P1')]

        self.assertEqual(
            3,
            len(self.registry.available_variables)
        )
        self.assertEqual(
            [['V1', 'T1', 'V2', 'T2'], ['T1', 'P1'], []],
            self.registry.available_variables
        )
        self.assertEqual(
            [{'PRESSURE': ['V1', 'T1', 'V2', 'T2']},
             {'PRESSURE': ['T1', 'P1']}, {}],
            self.registry.available_variables_by_type
        )

        self.data_source1.input_slot_info[0].name = 'V2'
        self.assertEqual(
            [['V2', 'T1', 'V2', 'T2'], ['T1', 'P1'], []],
            self.registry.available_variables
        )
        self.assertEqual(
            [{'PRESSURE': ['V2', 'T1', 'V2', 'T2']},
             {'PRESSURE': ['T1', 'P1']}, {}],
            self.registry.available_variables_by_type
        )

    def test_data_source_outputs(self):
        self.param1.name = 'V1'
        self.assertEqual(self.registry.data_source_outputs, [])

        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        self.assertEqual(self.registry.data_source_outputs, ["T1"])

        self.data_source2.output_slot_info = [OutputSlotInfo(name='T2')]
        self.assertEqual(self.registry.data_source_outputs, ["T1", "T2"])

    def test_data_source_inputs(self):
        self.param1.name = 'V1'
        self.assertEqual(self.registry.data_source_inputs, [])

        self.data_source1.input_slot_info = [InputSlotInfo(name='V1')]
        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        self.assertEqual(self.registry.data_source_inputs, ["V1"])

        self.data_source2.input_slot_info = [InputSlotInfo(name='T1')]
        self.data_source2.output_slot_info = [OutputSlotInfo(name='T2')]
        self.assertEqual(self.registry.data_source_inputs, ["V1", "T1"])
