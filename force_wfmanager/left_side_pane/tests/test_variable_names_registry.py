import unittest

from force_bdss.tests.probe_classes.mco import (
    ProbeParameterFactory, ProbeMCOFactory)
from force_bdss.tests.probe_classes.data_source import ProbeDataSourceFactory
from force_bdss.tests.probe_classes.kpi_calculator import (
    ProbeKPICalculatorFactory)
from force_bdss.core.workflow import Workflow

from force_wfmanager.left_side_pane.variable_names_registry import (
    VariableNamesRegistry)


class VariableNamesRegistryTest(unittest.TestCase):
    def setUp(self):
        workflow = Workflow()

        mco = ProbeMCOFactory(None).create_model()

        param_factory = ProbeParameterFactory(None)
        self.param1 = param_factory.create_model()
        self.param2 = param_factory.create_model()
        self.param3 = param_factory.create_model()

        data_source_factory = ProbeDataSourceFactory(
            None,
            input_slots_size=1,
            output_slots_size=1)
        self.data_source1 = data_source_factory.create_model()
        self.data_source2 = data_source_factory.create_model()

        kpi_factory = ProbeKPICalculatorFactory(
            None,
            input_slots_size=1,
            output_slots_size=1)
        kpi1 = kpi_factory.create_model()
        kpi2 = kpi_factory.create_model()

        workflow.mco = mco
        mco.parameters = [self.param1, self.param2, self.param3]
        workflow.data_sources = [self.data_source1, self.data_source2]
        workflow.kpi_calculators = [kpi1, kpi2]

        self.registry = VariableNamesRegistry(workflow=workflow)

    def test_registry_init(self):
        self.assertEqual(
            len(self.registry.data_source_available_variables), 0)
        self.assertEqual(
            len(self.registry.kpi_calculator_available_variables), 0)
        self.assertEqual(len(self.registry._mco_parameters_names), 0)
        self.assertEqual(len(self.registry._data_sources_outputs), 0)

    def test_available_names_update(self):
        self.param1.name = 'V1'
        self.assertEqual(self.registry._mco_parameters_names, ['V1'])

        self.param2.name = 'V2'
        self.assertEqual(self.registry._mco_parameters_names, ['V1', 'V2'])

        self.param3.name = 'V3'
        self.assertEqual(self.registry._mco_parameters_names,
                         ['V1', 'V2', 'V3'])

        self.param1.name = ''
        self.assertEqual(self.registry._mco_parameters_names,
                         ['V2', 'V3'])

        self.assertEqual(
            self.registry.data_source_available_variables,
            ['V2', 'V3'])
        self.assertEqual(
            self.registry.kpi_calculator_available_variables,
            ['V2', 'V3'])

        self.data_source1.output_slot_names = ['T1']
        self.data_source2.output_slot_names = ['T2']
        self.assertEqual(self.registry._data_sources_outputs,
                         ['T1', 'T2'])

        self.assertEqual(self.registry.data_source_available_variables,
                         ['V2', 'V3'])
        self.assertEqual(
            self.registry.kpi_calculator_available_variables,
            ['V2', 'V3', 'T1', 'T2'])
