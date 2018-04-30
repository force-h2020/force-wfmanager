import unittest

from traits.api import TraitError

from force_bdss.tests.probe_classes.data_source import \
    ProbeDataSourceFactory
from force_bdss.api import DataValue
from force_bdss.core.input_slot_info import InputSlotInfo

from force_wfmanager.left_side_pane.data_source_model_view import \
    DataSourceModelView
from force_wfmanager.left_side_pane.variable_names_registry import \
    VariableNamesRegistry


def get_run_function(nb_outputs):
    def run(*args, **kwargs):
        return [DataValue() for _ in range(nb_outputs)]
    return run


class TestEvaluatorModelView(unittest.TestCase):
    def setUp(self):
        kpi_factory = ProbeKPICalculatorFactory(
            None,
            input_slots_size=1,
            output_slots_size=2,
            run_function=get_run_function(2))

        self.kpi_model = kpi_factory.create_model()
        self.kpi_evaluator = kpi_factory.create_kpi_calculator()

        self.variable_names_registry = VariableNamesRegistry()
        self.variable_names_registry.data_source_available_variables = \
            ['P1']
        self.variable_names_registry.kpi_calculator_available_variables = \
            ['P1', 'P2', 'P3']

        self.kpi_mv = KPICalculatorModelView(
            model=self.kpi_model,
            variable_names_registry=self.variable_names_registry
        )

        data_source_factory = ProbeDataSourceFactory(
            None,
            input_slots_size=1,
            run_function=get_run_function(1))
        data_source_model = data_source_factory.create_model()
        self.data_source_mv = DataSourceModelView(
            model=data_source_model,
            variable_names_registry=self.variable_names_registry
        )

    def test_evaluator_model_view_init(self):
        self.assertEqual(self.kpi_mv.label, "test_kpi_calculator")
        self.assertIsInstance(
            self.kpi_mv._evaluator,
            BaseKPICalculator)
        self.assertEqual(len(self.kpi_mv.input_slots_representation), 1)
        self.assertEqual(len(self.kpi_mv.output_slots_representation), 2)
        self.assertEqual(self.kpi_model.input_slot_maps[0].name, '')
        self.assertEqual(self.kpi_model.output_slot_names[0], '')

    def test_input_slot_update(self):
        self.kpi_mv.input_slots_representation[0].name = 'P1'
        self.assertEqual(self.kpi_model.input_slot_maps[0].name, 'P1')

        self.variable_names_registry.kpi_calculator_available_variables = \
            ['P2', 'P3']
        self.assertEqual(self.kpi_model.input_slot_maps[0].name, '')

        self.kpi_mv.input_slots_representation[0].name = 'P2'
        self.assertEqual(self.kpi_model.input_slot_maps[0].name, 'P2')

        with self.assertRaises(TraitError):
            self.kpi_mv.input_slots_representation[0].name = 'P1'

    def test_output_slot_update(self):
        self.kpi_mv.output_slots_representation[0].name = 'output'
        self.assertEqual(self.kpi_model.output_slot_names[0], 'output')

    def test_bad_input_slots(self):
        input_slots, _ = self.kpi_evaluator.slots(self.kpi_model)

        self.kpi_model.input_slot_maps = [
            InputSlotMap(name='') for input_slot in range(len(input_slots) + 1)
        ]

        with self.assertRaisesRegexp(RuntimeError, "input slots"):
            KPICalculatorModelView(model=self.kpi_model)

    def test_bad_output_slots(self):
        _, output_slots = self.kpi_evaluator.slots(self.kpi_model)

        self.kpi_model.output_slot_names = (len(output_slots) + 1)*['']

        with self.assertRaisesRegexp(RuntimeError, "output slots"):
            KPICalculatorModelView(model=self.kpi_model)

    def test_update_table(self):
        self.kpi_model.output_slots_type = "bar"

        self.assertEqual(
            self.kpi_mv.output_slots_representation[0].type,
            "bar"
        )

        self.kpi_model.output_slot_names = ['p1', 't1']
        self.assertEqual(
            self.kpi_mv.output_slots_representation[0].name,
            'p1'
        )
        self.assertEqual(
            self.kpi_mv.output_slots_representation[1].name,
            't1'
        )

        self.kpi_model.input_slot_maps[0].name = 'P2'
        self.assertEqual(
            self.kpi_mv.input_slots_representation[0].name,
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
