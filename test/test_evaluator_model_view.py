import unittest
try:
    import mock
except ImportError:
    from unittest import mock

from traits.api import Instance

from envisage.plugin import Plugin

from force_bdss.core_plugins.dummy.kpi_adder.kpi_adder_calculator import \
    KPIAdderCalculator
from force_bdss.core_plugins.dummy.kpi_adder.kpi_adder_factory import \
    KPIAdderFactory
from force_bdss.core.input_slot_map import InputSlotMap

from force_wfmanager.left_side_pane.evaluator_model_view import \
    EvaluatorModelView


class BadEvaluatorModelView(EvaluatorModelView):
    model = Instance(KPIAdderFactory)


class EvaluatorModelViewTest(unittest.TestCase):
    def setUp(self):
        self.model = KPIAdderFactory(mock.Mock(spec=Plugin)).create_model()
        self.evaluator = KPIAdderFactory(
            mock.Mock(spec=Plugin)).create_kpi_calculator()

        self.evaluator_mv = EvaluatorModelView(model=self.model)

    def test_evaluator_model_view_init(self):
        self.assertEqual(self.evaluator_mv.label, "KPI Adder")
        self.assertIsInstance(
            self.evaluator_mv._evaluator,
            KPIAdderCalculator)
        self.assertEqual(len(self.evaluator_mv.output_slots_representation), 1)
        self.assertEqual(self.model.output_slot_names[0], '')

    def test_input_slot_update(self):
        self.evaluator_mv.input_slots_representation[0].name = 'input'
        self.assertEqual(self.model.input_slot_maps[0].name, 'input')

    def test_output_slot_update(self):
        self.evaluator_mv.output_slots_representation[0].name = 'output'
        self.assertEqual(self.model.output_slot_names[0], 'output')

    def test_bad_evaluator(self):
        with self.assertRaisesRegexp(TypeError, "The EvaluatorModelView needs "
                                                "a BaseDataSourceModel"):
            BadEvaluatorModelView(
                model=KPIAdderFactory(mock.Mock(spec=Plugin)))

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
        self.model.cuba_type_in = "foo"
        self.model.cuba_type_out = "bar"

        self.assertEqual(
            self.evaluator_mv.input_slots_representation[0].type,
            "foo"
        )
        self.assertEqual(
            self.evaluator_mv.output_slots_representation[0].type,
            "bar"
        )
