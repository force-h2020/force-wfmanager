import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from traits.api import Instance, Str, on_trait_change, TraitError

from envisage.plugin import Plugin

from force_bdss.api import (
    BaseKPICalculator, BaseKPICalculatorModel, BaseKPICalculatorFactory,
    BaseDataSource, BaseDataSourceModel, BaseDataSourceFactory,
    DataValue)
from force_bdss.core.slot import Slot
from force_bdss.core.input_slot_map import InputSlotMap

from force_wfmanager.left_side_pane.evaluator_model_view import \
    EvaluatorModelView
from force_wfmanager.left_side_pane.variable_names_registry import \
    VariableNamesRegistry


class KPICalculatorModel(BaseKPICalculatorModel):
    output_type = Str('PRESSURE')

    @on_trait_change('output_type')
    def update_slots(self):
        self.changes_slots = True


class KPICalculator(BaseKPICalculator):
    def run(self, model, data_source_results):
        return [DataValue(), DataValue()]

    def slots(self, model):
        return (
            Slot(type='PRESSURE'),
        ), (
            Slot(type=model.output_type),
            Slot(type='TEMPERATURE'),
        )


class KPICalculatorFactory(BaseKPICalculatorFactory):
    id = Str("enthought.test.kpi")
    name = "test_kpi"

    def create_model(self, model_data=None):
        return KPICalculatorModel(self)

    def create_kpi_calculator(self):
        return KPICalculator(self)


class DataSourceModel(BaseDataSourceModel):
    pass


class DataSource(BaseDataSource):
    def run(self, model, parameters):
        return [DataValue()]

    def slots(self, model):
            return (Slot(type='PRESSURE'), ), ()


class DataSourceFactory(BaseDataSourceFactory):
    id = Str("enthought.test.datasource")
    name = "test_datasource"

    def create_model(self, model_data=None):
        return DataSourceModel(self)

    def create_data_source(self):
        return DataSource(self)


class BadEvaluatorModelView(EvaluatorModelView):
    model = Instance(KPICalculatorFactory)


class TestEvaluatorModelView(unittest.TestCase):
    def setUp(self):
        factory = KPICalculatorFactory(mock.Mock(spec=Plugin))

        self.model = factory.create_model()
        self.evaluator = factory.create_kpi_calculator()

        self.variable_names_registry = VariableNamesRegistry()
        self.variable_names_registry.data_source_available_variables = \
            ['P1']
        self.variable_names_registry.kpi_calculator_available_variables = \
            ['P1', 'P2', 'P3']

        self.evaluator_mv = EvaluatorModelView(
            model=self.model,
            variable_names_registry=self.variable_names_registry
        )

        data_source_factory = DataSourceFactory(mock.Mock(spec=Plugin))

        data_source_model = data_source_factory.create_model()

        self.data_source_mv = EvaluatorModelView(
            model=data_source_model,
            variable_names_registry=self.variable_names_registry
        )

    def test_evaluator_model_view_init(self):
        self.assertEqual(self.evaluator_mv.label, "test_kpi")
        self.assertIsInstance(
            self.evaluator_mv._evaluator,
            KPICalculator)
        self.assertEqual(len(self.evaluator_mv.input_slots_representation), 1)
        self.assertEqual(len(self.evaluator_mv.output_slots_representation), 2)
        self.assertEqual(self.model.input_slot_maps[0].name, '')
        self.assertEqual(self.model.output_slot_names[0], '')

    def test_input_slot_update(self):
        self.evaluator_mv.input_slots_representation[0].name = 'P1'
        self.assertEqual(self.model.input_slot_maps[0].name, 'P1')

        self.variable_names_registry.kpi_calculator_available_variables = \
            ['P2', 'P3']
        self.assertEqual(self.model.input_slot_maps[0].name, '')

        self.evaluator_mv.input_slots_representation[0].name = 'P2'
        self.assertEqual(self.model.input_slot_maps[0].name, 'P2')

        with self.assertRaises(TraitError):
            self.evaluator_mv.input_slots_representation[0].name = 'P1'

    def test_output_slot_update(self):
        self.evaluator_mv.output_slots_representation[0].name = 'output'
        self.assertEqual(self.model.output_slot_names[0], 'output')

    def test_bad_evaluator(self):
        with self.assertRaisesRegexp(TypeError, "The EvaluatorModelView needs "
                                                "a BaseDataSourceModel"):
            BadEvaluatorModelView(
                model=KPICalculatorFactory(mock.Mock(spec=Plugin)))

    def test_bad_input_slots(self):
        input_slots, _ = self.evaluator.slots(self.model)

        self.model.input_slot_maps = [
            InputSlotMap(name='') for input_slot in range(len(input_slots) + 1)
        ]

        with self.assertRaisesRegexp(RuntimeError, "input slots"):
            EvaluatorModelView(model=self.model)

    def test_bad_output_slots(self):
        _, output_slots = self.evaluator.slots(self.model)

        self.model.output_slot_names = (len(output_slots) + 1)*['']

        with self.assertRaisesRegexp(RuntimeError, "output slots"):
            EvaluatorModelView(model=self.model)

    def test_update_table(self):
        self.model.output_type = "bar"

        self.assertEqual(
            self.evaluator_mv.output_slots_representation[0].type,
            "bar"
        )

        self.model.output_slot_names = ['p1', 't1']
        self.assertEqual(
            self.evaluator_mv.output_slots_representation[0].name,
            'p1'
        )
        self.assertEqual(
            self.evaluator_mv.output_slots_representation[1].name,
            't1'
        )

        self.model.input_slot_maps[0].name = 'P2'
        self.assertEqual(
            self.evaluator_mv.input_slots_representation[0].name,
            'P2'
        )

    def test_update_data_source_table(self):
        slots = self.data_source_mv.input_slots_representation
        self.assertEqual(
            slots[0].available_variables,
            ['P1']
        )

        self.variable_names_registry.data_source_available_variables = ['P2']
        self.assertEqual(
            slots[0].available_variables,
            ['P2']
        )
