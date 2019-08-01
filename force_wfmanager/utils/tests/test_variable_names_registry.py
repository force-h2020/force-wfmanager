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

    def test_available_variables(self):
        self.data_source1.input_slot_info = [InputSlotInfo(name='V1')]
        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]

        self.assertEqual(2, len(self.registry.available_variables))
        self.assertEqual('T1', self.registry.available_variables[0].name)
        self.assertEqual('V1', self.registry.available_variables[1].name)

    def test_available_variable_names(self):

        self.data_source1.input_slot_info = [InputSlotInfo(name='V1')]
        self.data_source2.input_slot_info = [InputSlotInfo(name='V2')]
        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        self.data_source2.output_slot_info = [OutputSlotInfo(name='T2')]

        self.data_source3.input_slot_info = [InputSlotInfo(name='T1')]
        self.data_source3.output_slot_info = [OutputSlotInfo(name='P1')]

        self.assertEqual(
            4,
            len(self.registry.available_variable_names)
        )
        self.assertEqual(
            [['V1', 'V2'],
             ['T1', 'T2', 'V1', 'V2'],
             ['T1', 'T2', 'P1', 'V1', 'V2'],
             ['T1', 'T2', 'P1', 'V1', 'V2']],
            self.registry.available_variable_names
        )

    def test_available_variables_by_type(self):

        self.data_source1.input_slot_info = [InputSlotInfo(name='V1')]
        self.data_source2.input_slot_info = [InputSlotInfo(name='V2')]
        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        self.data_source2.output_slot_info = [OutputSlotInfo(name='T2')]

        self.data_source3.input_slot_info = [InputSlotInfo(name='T1')]
        self.data_source3.output_slot_info = [OutputSlotInfo(name='P1')]

        self.assertEqual(
            4,
            len(self.registry.available_variables_by_type)
        )
        self.assertEqual(
            {'PRESSURE'},
            self.registry.available_variables_by_type[0].keys()
        )
        self.assertEqual(
            2,
            len(self.registry.available_variables_by_type[0]["PRESSURE"])
        )
        self.assertEqual(
            {'PRESSURE'},
            self.registry.available_variables_by_type[1].keys()
        )
        self.assertEqual(
            2,
            len(self.registry.available_variables_by_type[1]["PRESSURE"])
        )
        self.assertEqual(
            {'PRESSURE'},
            self.registry.available_variables_by_type[2].keys()
        )
        self.assertEqual(
            1,
            len(self.registry.available_variables_by_type[2]["PRESSURE"])
        )

    def test_update__variable_registry(self):
        registry = self.registry._variable_registry
        self.assertEqual(2, len(registry))

        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        self.data_source3.input_slot_info = [InputSlotInfo(name='T1')]
        variable_list = self.registry.available_variables

        self.assertEqual(1, len(variable_list))
        self.assertEqual('PRESSURE T1', variable_list[0].label)
        self.assertIsNotNone(variable_list[0].output_slot)
        self.assertEqual(1, len(variable_list[0].input_slots))

        self.data_source1.input_slot_info = [InputSlotInfo(name='V1')]
        variable_list = self.registry.available_variables

        self.assertEqual(2, len(variable_list))
        self.assertEqual('PRESSURE V1', variable_list[1].label)
        self.assertIsNone(variable_list[1].output_slot)
        self.assertIn('V1:PRESSURE', registry['undefined'])

        self.data_source3.output_slot_info = [OutputSlotInfo(name='P1')]
        variable_list = self.registry.available_variables

        self.assertEqual('PRESSURE P1', variable_list[1].label)
        self.assertIsNotNone(variable_list[1].output_slot)
        self.assertIn('V1:PRESSURE', registry['undefined'])

        # Rename an output variable
        self.data_source1.output_slot_info[0].name = 'B1'
        variable_list = self.registry.available_variables

        self.assertEqual(3, len(variable_list))
        self.assertEqual('PRESSURE B1', variable_list[0].label)
        self.assertEqual('PRESSURE P1', variable_list[1].label)
        self.assertIsNotNone(variable_list[0].output_slot)
        self.assertIsNone(variable_list[2].output_slot)

        # Rename an input variable
        self.data_source3.input_slot_info[0].name = 'C1'
        variable_list = self.registry.available_variables

        self.assertEqual(4, len(variable_list))
        self.assertEqual('PRESSURE C1', variable_list[3].label)
        self.assertIsNone(variable_list[3].output_slot)
        self.assertEqual(0, len(variable_list[0].input_slots))

        # Clean an output variable name
        self.data_source1.output_slot_info[0].name = ''
        variable_list = self.registry.available_variables

        self.assertEqual(3, len(variable_list))
        self.assertEqual('PRESSURE P1', variable_list[0].label)
        self.assertEqual('PRESSURE V1', variable_list[1].label)
        self.assertEqual('PRESSURE C1', variable_list[2].label)
        self.assertIsNotNone(variable_list[0].output_slot)
        self.assertIsNone(variable_list[1].output_slot)
        self.assertIsNone(variable_list[2].output_slot)

        # Clean an input variable name
        self.data_source3.input_slot_info[0].name = ''
        variable_list = self.registry.available_variables

        self.assertEqual(2, len(variable_list))
        self.assertEqual('PRESSURE P1', variable_list[0].label)
        self.assertEqual('PRESSURE V1', variable_list[1].label)
        self.assertIsNotNone(variable_list[0].output_slot)
        self.assertIsNone(variable_list[1].output_slot)


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
            output_slot=data_source.output_slot_info[0],
        )

    def test_label(self):
        self.assertEqual('PRESSURE T1', self.variable.label)
        self.variable.name = 'P1'
        self.assertEqual('PRESSURE P1', self.variable.label)
        self.variable.output_slot.name = 'B1'
        self.assertEqual('PRESSURE B1', self.variable.label)

    def test_verify(self):
        errors = self.variable.verify()
        self.assertEqual(0, len(errors))

        self.variable.input_slots.append((1, InputSlotInfo()))

        errors = self.variable.verify()
        self.assertEqual(0, len(errors))

        self.variable.input_slots.append((0, InputSlotInfo()))

        errors = self.variable.verify()
        self.assertEqual(1, len(errors))
        self.assertIn(
            'Variable is being used as an input before being generated',
            errors[0].local_error)

    def test_update_name(self):
        self.variable.input_slots.append((1, InputSlotInfo(name='T1')))
        self.variable.output_slot.name = 'V1'

        self.assertEqual('V1', self.variable.input_slots[0][1].name)

    def test_check_input_slot_hook(self):
        input_slot = InputSlotInfo(name='T1')

        self.assertTrue(self.variable.check_input_slot_hook(
            input_slot, 'PRESSURE', 0)
        )
        input_slot = InputSlotInfo(name='C1')
        self.assertFalse(self.variable.check_input_slot_hook(
            input_slot, 'VOLUME', 0)
        )
        self.assertEqual(1, len(self.variable.input_slots))
