import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from force_bdss.api import (
    BaseMCOParameter, BaseMCOParameterFactory,
    BaseMCOModel, BaseMCOFactory,
    BaseDataSourceModel, BaseDataSourceFactory, BaseDataSource,
    BaseKPICalculatorModel, BaseKPICalculatorFactory, BaseKPICalculator)
from force_bdss.core.slot import Slot
from force_bdss.core.workflow import Workflow

from force_wfmanager.left_side_pane.variable_names_registry import (
    VariableNamesRegistry)


class DummyParameterModel(BaseMCOParameter):
    pass


class DummyMCOModel(BaseMCOModel):
    pass


class DummyDataSourceModel(BaseDataSourceModel):
    pass


class DummyKPIModel(BaseKPICalculatorModel):
    pass


def create_parameter_model():
    factory = mock.Mock(spec=BaseMCOParameterFactory)
    return DummyParameterModel(factory=factory)


def create_mco_model():
    factory = mock.Mock(spec=BaseMCOFactory)
    return DummyMCOModel(factory=factory)


def create_data_source_model():
    factory = mock.Mock(spec=BaseDataSourceFactory)
    data_source = mock.Mock(spec=BaseDataSource)

    def slots(*args, **kwargs):
        return (
            (Slot(type='P'), ),
            (Slot(type='T'), )
        )
    data_source.slots = slots

    factory.create_data_source = lambda: data_source
    return DummyDataSourceModel(factory=factory)


def create_kpi_model():
    factory = mock.Mock(spec=BaseKPICalculatorFactory)
    kpi_calculator = mock.Mock(spec=BaseKPICalculator)

    def slots(*args, **kwargs):
        return (
            (Slot(type='P'), ),
            (Slot(type='T'), )
        )
    kpi_calculator.slots = slots

    factory.create_kpi_calculator = lambda: kpi_calculator
    return DummyKPIModel(factory=factory)


class VariableNamesRegistryTest(unittest.TestCase):
    def setUp(self):
        workflow = Workflow()

        mco = create_mco_model()

        self.param1 = create_parameter_model()
        self.param2 = create_parameter_model()
        self.param3 = create_parameter_model()

        self.data_source1 = create_data_source_model()
        self.data_source2 = create_data_source_model()

        kpi1 = create_kpi_model()
        kpi2 = create_kpi_model()

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
