import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from force_bdss.api import (
    BaseMCOParameter, BaseMCOParameterFactory,
    BaseDataSourceModel, BaseDataSourceFactory, BaseDataSource,
    BaseKPICalculatorModel, BaseKPICalculatorFactory, BaseKPICalculator)
from force_bdss.core.slot import Slot

from force_wfmanager.left_side_pane.mco_parameter_model_view import (
    MCOParameterModelView)
from force_wfmanager.left_side_pane.data_source_model_view import (
    DataSourceModelView)
from force_wfmanager.left_side_pane.variable_names_register import (
    VariableNamesRegister)


class DummyParameterModel(BaseMCOParameter):
    pass


class DummyDataSourceModel(BaseDataSourceModel):
    pass


class DummyKPIModel(BaseKPICalculatorModel):
    pass


def create_parameter_model():
    factory = mock.Mock(spec=BaseMCOParameterFactory)
    return DummyParameterModel(factory=factory)


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


class VariableNamesRegisterTest(unittest.TestCase):
    def setUp(self):
        self.register = VariableNamesRegister()

        self.param1 = create_parameter_model()
        self.param2 = create_parameter_model()
        self.param3 = create_parameter_model()

        self.register.mco_parameters_mv = [
            MCOParameterModelView(model=self.param1),
            MCOParameterModelView(model=self.param2),
            MCOParameterModelView(model=self.param3),
        ]

        self.data_source1 = create_data_source_model()
        self.data_source2 = create_data_source_model()

        self.register.data_sources_mv = [
            DataSourceModelView(model=self.data_source1),
            DataSourceModelView(model=self.data_source2),
        ]

    def test_register_init(self):
        self.assertEqual(len(self.register.mco_parameters_mv), 3)
        self.assertEqual(len(self.register.mco_parameters_names), 0)
        self.assertEqual(len(self.register.data_sources_mv), 2)
        self.assertEqual(len(self.register.data_sources_output_names), 0)
        self.assertEqual(len(self.register.kpi_calculators_mv), 0)

    def test_available_names_update(self):
        self.assertEqual(self.register.mco_parameters_names, [])

        self.param1.name = 'V1'
        self.assertEqual(self.register.mco_parameters_names, ['V1'])

        self.param2.name = 'V2'
        self.assertEqual(self.register.mco_parameters_names, ['V1', 'V2'])

        self.param3.name = 'V3'
        self.assertEqual(self.register.mco_parameters_names,
                         ['V1', 'V2', 'V3'])

        self.param1.name = ''
        self.assertEqual(self.register.mco_parameters_names,
                         ['V2', 'V3'])
        self.assertEqual(self.register.data_sources_mv[0].available_variables,
                         ['V2', 'V3'])

        self.data_source1.output_slot_names = ['T1']
        self.data_source2.output_slot_names = ['T2']
        self.assertEqual(self.register.data_sources_output_names,
                         ['T1', 'T2'])
