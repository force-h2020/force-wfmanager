import unittest

from force_bdss.api import OutputSlotInfo, ExecutionLayer
from force_bdss.tests.probe_classes.mco import (
    ProbeParameterFactory, ProbeMCOFactory)
from force_bdss.tests.probe_classes.data_source import ProbeDataSourceFactory
from force_bdss.core.workflow import Workflow
from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin

from force_wfmanager.left_side_pane.variable_names_registry import (
    VariableNamesRegistry)


def basic_variable_names_registry():
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
        self.registry = basic_variable_names_registry()
        self.workflow = self.registry.workflow
        self.param1 = self.workflow.mco.parameters[0]
        self.param2 = self.workflow.mco.parameters[1]
        self.param3 = self.workflow.mco.parameters[2]
        self.data_source1 = self.workflow.execution_layers[0].data_sources[0]
        self.data_source2 = self.workflow.execution_layers[0].data_sources[1]
        self.data_source3 = self.workflow.execution_layers[1].data_sources[0]
        self.data_source4 = self.workflow.execution_layers[2].data_sources[0]

    def test_registry_init(self):
        self.assertEqual(len(self.registry.available_variables_stack), 4)

    def test_available_names_update(self):
        self.param1.name = 'V1'
        self.assertEqual(self.registry.available_variables_stack[0],
                         [{'type': '', 'name': 'V1'}])

        self.param2.name = 'V2'
        self.assertEqual(self.registry.available_variables_stack[0],
                         [{'type': '', 'name': 'V1'},
                          {'type': '', 'name': 'V2'}])

        self.param3.name = 'V3'
        self.assertEqual(self.registry.available_variables_stack[0],
                         [{'type': '', 'name': 'V1'},
                          {'type': '', 'name': 'V2'},
                          {'type': '', 'name': 'V3'}])

        self.param1.name = ''
        self.assertEqual(self.registry.available_variables_stack[0],
                         [{'type': '', 'name': 'V2'},
                          {'type': '', 'name': 'V3'}])

        self.assertEqual(self.registry.available_variables_stack[1], [])
        self.assertEqual(self.registry.available_variables_stack[2], [])

        self.data_source1.output_slot_info = [OutputSlotInfo(name='T1')]
        self.data_source2.output_slot_info = [OutputSlotInfo(name='T2')]
        self.assertEqual(
            self.registry.available_variables_stack[1],
            [{'type': 'PRESSURE', 'name': 'T1'},
             {'type': 'PRESSURE', 'name': 'T2'}])

        self.data_source2.output_slot_info[0].name = 'T4'
        self.assertEqual(
            self.registry.available_variables_stack[1],
            [{'type': 'PRESSURE', 'name': 'T1'},
             {'type': 'PRESSURE', 'name': 'T4'}])

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
