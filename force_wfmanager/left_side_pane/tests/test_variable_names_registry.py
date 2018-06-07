import unittest

from force_bdss.core.execution_layer import ExecutionLayer
from force_bdss.core.output_slot_info import OutputSlotInfo
from force_bdss.tests.probe_classes.mco import (
    ProbeParameterFactory, ProbeMCOFactory)
from force_bdss.tests.probe_classes.data_source import ProbeDataSourceFactory
from force_bdss.core.workflow import Workflow
from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin

from force_wfmanager.left_side_pane.variable_names_registry import (
    VariableNamesRegistry)


class VariableNamesRegistryTest(unittest.TestCase):
    def setUp(self):
        self.plugin = ProbeExtensionPlugin()
        workflow = Workflow()

        mco_factory = ProbeMCOFactory(self.plugin)
        mco = mco_factory.create_model()

        param_factory = ProbeParameterFactory(mco_factory)
        self.param1 = param_factory.create_model()
        self.param2 = param_factory.create_model()
        self.param3 = param_factory.create_model()

        data_source_factory = ProbeDataSourceFactory(
            self.plugin,
            input_slots_size=1,
            output_slots_size=1)
        # first layer
        self.data_source1 = data_source_factory.create_model()
        self.data_source2 = data_source_factory.create_model()

        # second layer
        self.data_source3 = data_source_factory.create_model()

        # third layer
        self.data_source4 = data_source_factory.create_model()

        workflow.mco = mco
        mco.parameters = [self.param1, self.param2, self.param3]
        workflow.execution_layers.extend([
            ExecutionLayer(
                data_sources=[self.data_source1, self.data_source2]
            ),
            ExecutionLayer(
                data_sources=[self.data_source3]
            ),
            ExecutionLayer(
                data_sources=[self.data_source3]
            )
            ]
        )

        self.registry = VariableNamesRegistry(workflow=workflow)

    def test_registry_init(self):
        self.assertEqual(len(self.registry.available_variables_stack), 4)

    def test_available_names_update(self):
        self.param1.name = 'V1'
        self.assertEqual(self.registry.available_variables_stack[0], ['V1'])

        self.param2.name = 'V2'
        self.assertEqual(self.registry.available_variables_stack[0],
                         ['V1', 'V2'])

        self.param3.name = 'V3'
        self.assertEqual(self.registry.available_variables_stack[0],
                         ['V1', 'V2', 'V3'])

        self.param1.name = ''
        self.assertEqual(self.registry.available_variables_stack[0],
                         ['V2', 'V3'])

        self.assertEqual(self.registry.available_variables_stack[1], [])
        self.assertEqual(self.registry.available_variables_stack[2], [])

        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        self.data_source2.output_slot_info = [OutputSlotInfo(name='T2')]
        self.assertEqual(
            self.registry.available_variables_stack[1],
            ['T1', 'T2'])

        self.data_source2.output_slot_info[0].name = 'T4'
        self.assertEqual(
            self.registry.available_variables_stack[1],
            ['T1', 'T4'])

        self.assertEqual(
            self.registry.available_variables,
            [
                ['V2', 'V3'],
                ['V2', 'V3', 'T1', 'T4'],
                ['V2', 'V3', 'T1', 'T4'],
                ['V2', 'V3', 'T1', 'T4']
            ])

    def test_data_source_outputs(self):
        self.param1.name = 'V1'
        self.assertEqual(self.registry.data_source_outputs, [])

        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        self.assertEqual(self.registry.data_source_outputs, ["T1"])

        self.data_source2.output_slot_info = [OutputSlotInfo(name='T2')]
        self.assertEqual(self.registry.data_source_outputs, ["T1", "T2"])
