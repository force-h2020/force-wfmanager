import unittest

from force_bdss.api import ExecutionLayer
from force_bdss.core.workflow import Workflow
from force_bdss.tests.probe_classes.data_source import (
    ProbeDataSourceFactory
)
from force_bdss.tests.probe_classes.mco import (
    ProbeParameterFactory, ProbeMCOFactory
)
from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin

from force_wfmanager.ui.setup.process.process_view import ProcessView
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)


def get_basic_workflow():
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

    return workflow


class VariableNamesRegistryTest(unittest.TestCase):
    def setUp(self):
        self.workflow = get_basic_workflow()
        self.param1 = self.workflow.mco.parameters[0]
        self.param2 = self.workflow.mco.parameters[1]
        self.param3 = self.workflow.mco.parameters[2]
        self.data_source1 = self.workflow.execution_layers[0].data_sources[0]
        self.data_source2 = self.workflow.execution_layers[0].data_sources[1]
        self.data_source3 = self.workflow.execution_layers[1].data_sources[0]
        self.data_source4 = self.workflow.execution_layers[2].data_sources[0]

        self.process_view = ProcessView(model=self.workflow)

        self.registry = VariableNamesRegistry(
            process_view=self.process_view
        )

    def test_available_variables(self):
        self.data_source1.input_slot_info[0].name = 'V1'
        self.data_source1.output_slot_info[0].name = 'T1'

        self.assertEqual(2, len(self.registry.available_variables))
        self.assertEqual('T1', self.registry.available_variables[0].name)
        self.assertEqual('V1', self.registry.available_variables[1].name)

    def test_available_variable_names(self):
        self.data_source1.input_slot_info[0].name = 'V1'
        self.data_source2.input_slot_info[0].name = 'V2'

        self.data_source1.output_slot_info[0].name = 'T1'
        self.data_source2.output_slot_info[0].name = 'T2'

        self.data_source3.input_slot_info[0].name = 'T1'
        self.data_source3.output_slot_info[0].name = 'P1'

        self.assertEqual(
            4,
            len(self.registry.available_variable_names)
        )

        self.assertListEqual(
            ['V1', 'V2'], self.registry.available_variable_names[0])
        self.assertListEqual(
            ['T1', 'T2', 'V1', 'V2'],
            self.registry.available_variable_names[1])
        self.assertListEqual(
            ['T1', 'T2', 'P1', 'V1', 'V2'],
            self.registry.available_variable_names[2])
        self.assertListEqual(
            ['T1', 'T2', 'P1', 'V1', 'V2'],
            self.registry.available_variable_names[3])

    def test_available_variables_by_type(self):
        self.data_source1.input_slot_info[0].name = 'V1'
        self.data_source2.input_slot_info[0].name = 'V2'
        self.data_source1.output_slot_info[0].name = 'T1'
        self.data_source2.output_slot_info[0].name = 'T2'

        self.data_source3.input_slot_info[0].name = 'T1'
        self.data_source3.output_slot_info[0].name = 'P1'

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

        self.data_source1.output_slot_info[0].name = 'T1'
        self.data_source3.input_slot_info[0].name = 'T1'

        variable_list = self.registry.available_variables

        self.assertEqual(1, len(variable_list))
        self.assertEqual('PRESSURE T1', variable_list[0].label)
        self.assertIsNotNone(variable_list[0].output_slot_info)
        self.assertEqual(1, len(variable_list[0].input_slot_rows))

        self.data_source1.input_slot_info[0].name = 'V1'
        variable_list = self.registry.available_variables

        self.assertEqual(2, len(variable_list))
        self.assertEqual('PRESSURE V1', variable_list[1].label)
        self.assertIsNone(variable_list[1].output_slot_info)
        self.assertIn(('V1', 'PRESSURE'), registry['undefined'])

        self.data_source3.output_slot_info[0].name = 'P1'
        variable_list = self.registry.available_variables

        self.assertEqual('PRESSURE P1', variable_list[1].label)
        self.assertIsNotNone(variable_list[1].output_slot_info)
        self.assertIn(('V1', 'PRESSURE'), registry['undefined'])

    def test_rename_variables(self):

        self.data_source1.output_slot_info[0].name = 'T1'
        self.data_source3.input_slot_info[0].name = 'T1'
        self.data_source3.output_slot_info[0].name = 'P1'
        variable_list = self.registry.available_variables
        self.assertEqual(2, len(variable_list))

        # Rename an output variable
        self.data_source1.output_slot_info[0].name = 'B1'
        variable_list = self.registry.available_variables

        self.assertEqual(2, len(variable_list))
        self.assertEqual('PRESSURE B1', variable_list[0].label)
        self.assertEqual('PRESSURE P1', variable_list[1].label)
        self.assertIsNotNone(variable_list[0].output_slot_info)
        self.assertIsNotNone(variable_list[1].output_slot_info)
        self.assertEqual(
            'B1', self.data_source3.input_slot_info[0].name
        )

        # Rename an input variable
        self.data_source3.input_slot_info[0].name = 'C1'
        variable_list = self.registry.available_variables

        self.assertEqual(3, len(variable_list))
        self.assertEqual('PRESSURE C1', variable_list[2].label)
        self.assertIsNone(variable_list[2].output_slot_info)
        self.assertEqual(0, len(variable_list[0].input_slot_rows))

        # Revert to original input variable name
        self.data_source3.input_slot_info[0].name = 'B1'
        variable_list = self.registry.available_variables

        self.assertEqual(2, len(variable_list))
        self.assertEqual('PRESSURE B1', variable_list[0].label)
        self.assertEqual('PRESSURE P1', variable_list[1].label)
        self.assertIsNotNone(variable_list[0].output_slot_info)
        self.assertIsNotNone(variable_list[1].output_slot_info)
        self.assertEqual(
            'B1', self.data_source3.input_slot_info[0].name
        )

    def test_clear_variable_names(self):
        self.data_source1.output_slot_info[0].name = 'T1'
        self.data_source3.input_slot_info[0].name = 'T1'
        self.data_source3.output_slot_info[0].name = 'P1'
        variable_list = self.registry.available_variables
        self.assertEqual(2, len(variable_list))

        # Clear an output variable name
        self.data_source1.output_slot_info[0].name = ''
        variable_list = self.registry.available_variables
        self.assertEqual(1, len(variable_list))
        self.assertEqual('PRESSURE P1', variable_list[0].label)
        self.assertIsNotNone(variable_list[0].output_slot_info)

        # Clear an input variable name
        self.data_source3.input_slot_info[0].name = ''
        variable_list = self.registry.available_variables
        self.assertEqual(1, len(variable_list))
        self.assertEqual('PRESSURE P1', variable_list[0].label)
        self.assertIsNotNone(variable_list[0].output_slot_info)