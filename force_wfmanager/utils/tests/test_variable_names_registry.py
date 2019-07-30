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
    Variable, VariableNamesRegistry
)


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

        self.assertEqual([('V1', 'PRESSURE')],
                         self.registry.available_input_variables_stack[0])
        self.assertEqual([('T1', 'PRESSURE')],
                         self.registry.available_output_variables_stack[0])

        self.data_source2.input_slot_info = [InputSlotInfo(name='V2')]
        self.data_source2.output_slot_info = [OutputSlotInfo(name='T2')]

        self.assertEqual([('V1', 'PRESSURE'),
                          ('V2', 'PRESSURE')],
                         self.registry.available_input_variables_stack[0])
        self.assertEqual([('T1', 'PRESSURE'),
                          ('T2', 'PRESSURE')],
                         self.registry.available_output_variables_stack[0])

        self.data_source3.input_slot_info = [InputSlotInfo(name='T1')]
        self.data_source3.output_slot_info = [OutputSlotInfo(name='T3')]
        self.assertEqual([('T1', 'PRESSURE')],
                         self.registry.available_input_variables_stack[1])
        self.assertEqual([('T3', 'PRESSURE')],
                         self.registry.available_output_variables_stack[1])

        self.data_source3.input_slot_info = [InputSlotInfo(name='')]
        self.data_source3.changes_slots = True
        self.data_source3.output_slot_info = [OutputSlotInfo(name='T3')]
        self.assertEqual([],
                         self.registry.available_input_variables_stack[1])

    def test_available_variables(self):

        self.data_source1.input_slot_info = [InputSlotInfo(name='V1')]
        self.data_source2.input_slot_info = [InputSlotInfo(name='V2')]
        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        self.data_source2.output_slot_info = [OutputSlotInfo(name='T2')]

        self.data_source3.input_slot_info = [InputSlotInfo(name='T1')]
        self.data_source3.output_slot_info = [OutputSlotInfo(name='P1')]

        self.assertEqual(
            4,
            len(self.registry.available_variables)
        )
        self.assertEqual(
            [[''], ['V1', 'V2', 'T1', 'T2'], ['T1', 'P1'], []],
            self.registry.available_variables
        )

    def test_data_source_outputs(self):
        self.param1.name = 'V1'
        self.assertEqual(self.registry.data_source_outputs, [])

        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        self.assertEqual([("T1", 'PRESSURE')],
                         self.registry.data_source_outputs)

        self.data_source2.output_slot_info = [OutputSlotInfo(name='T2')]
        self.assertEqual([("T1", 'PRESSURE'),
                          ("T2", 'PRESSURE')],
                         self.registry.data_source_outputs, )

    def test_data_source_inputs(self):
        self.param1.name = 'V1'
        self.assertEqual(self.registry.data_source_inputs, [])

        self.data_source1.input_slot_info = [InputSlotInfo(name='V1')]
        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        self.assertEqual([("V1", 'PRESSURE')],
                         self.registry.data_source_inputs)

        self.data_source2.input_slot_info = [InputSlotInfo(name='T1')]
        self.data_source2.output_slot_info = [OutputSlotInfo(name='T2')]
        self.assertEqual([("V1", 'PRESSURE'),
                          ("T1", 'PRESSURE')],
                         self.registry.data_source_inputs)

    def test_update_variable_registry(self):
        database = self.registry.variable_registry

        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        self.data_source3.input_slot_info = [InputSlotInfo(name='T1')]

        variable_list = list(database.values())
        self.assertEqual(1, len(variable_list))
        self.assertEqual('PRESSURE T1', variable_list[0].label)
        self.assertIsNotNone(variable_list[0].origin)
        self.assertEqual(1, len(variable_list[0].input_slots))

        self.data_source1.input_slot_info = [InputSlotInfo(name='V1')]

        variable_list = list(database.values())
        self.assertEqual('PRESSURE V1', variable_list[1].label)
        self.assertIsNone(variable_list[1].origin)
        self.assertIn('V1:PRESSURE', database.keys())

        self.data_source3.output_slot_info = [OutputSlotInfo(name='P1')]

        variable_list = list(database.values())
        self.assertEqual('PRESSURE P1', variable_list[2].label)
        self.assertIsNotNone(variable_list[2].origin)

        # Rename an output variable
        self.data_source1.output_slot_info[0].name = 'B1'

        variable_list = list(database.values())
        self.assertEqual(3, len(variable_list))
        self.assertEqual('PRESSURE B1', variable_list[0].label)
        self.assertEqual('PRESSURE P1', variable_list[2].label)
        self.assertIsNotNone(variable_list[2].origin)
        self.assertIsNone(variable_list[1].origin)

        # Rename an input variable
        self.data_source3.input_slot_info[0].name = 'C1'

        variable_list = list(database.values())
        self.assertEqual(4, len(variable_list))
        self.assertEqual('PRESSURE C1', variable_list[3].label)
        self.assertIsNone(variable_list[3].origin)
        self.assertEqual(0, len(variable_list[0].input_slots))


class VariableTest(unittest.TestCase):

    def setUp(self):
        plugin = ProbeExtensionPlugin()
        self.data_source_factory = ProbeDataSourceFactory(
            plugin,
            input_slots_size=1,
            output_slots_size=1)

        data_source = self.data_source_factory.create_model()
        data_source.output_slot_info = [OutputSlotInfo(name='T1')]

        self.variable = Variable(
            type='PRESSURE',
            layer=0,
            origin=data_source,
            origin_slot=data_source.output_slot_info[0],
        )

    def test_label(self):
        self.assertEqual('PRESSURE T1', self.variable.label)
        self.variable.name = 'P1'
        self.assertEqual('PRESSURE P1', self.variable.label)
        self.variable.origin_slot.name = 'B1'
        self.assertEqual('PRESSURE B1', self.variable.label)

    def test_verify_generation(self):
        errors = self.variable.verify_generation()
        self.assertEqual(0, len(errors))

        self.variable.input_slots.append((1, InputSlotInfo()))

        errors = self.variable.verify_generation()
        self.assertEqual(0, len(errors))

        self.variable.input_slots.append((0, InputSlotInfo()))

        errors = self.variable.verify_generation()
        self.assertEqual(1, len(errors))
        self.assertIn(
            'Variable is being used as an input before being generated',
            errors[0].global_error)

    def test_update_name(self):
        self.variable.input_slots.append((1, InputSlotInfo(name='T1')))
        self.variable.origin_slot.name = 'V1'

        self.assertEqual('V1', self.variable.input_slots[0][1].name)
