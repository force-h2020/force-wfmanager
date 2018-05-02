import unittest

from traits.api import TraitError

from force_bdss.core.execution_layer import ExecutionLayer
from force_bdss.core.output_slot_info import OutputSlotInfo
from force_bdss.core.workflow import Workflow
from force_bdss.data_sources.base_data_source_model import BaseDataSourceModel
from force_bdss.tests.probe_classes.data_source import \
    ProbeDataSourceFactory
from force_bdss.api import DataValue
from force_bdss.core.input_slot_info import InputSlotInfo
from force_bdss.tests.probe_classes.mco import ProbeMCOFactory, ProbeParameter

from force_wfmanager.left_side_pane.data_source_model_view import \
    DataSourceModelView
from force_wfmanager.left_side_pane.variable_names_registry import \
    VariableNamesRegistry


def get_run_function(nb_outputs):
    def run(*args, **kwargs):
        return [DataValue() for _ in range(nb_outputs)]
    return run


class TestDataSourceModelView(unittest.TestCase):
    def setUp(self):
        factory = ProbeDataSourceFactory(
            None,
            input_slots_size=1,
            output_slots_size=2,
            run_function=get_run_function(2))

        self.model_1 = factory.create_model()
        self.data_source = factory.create_data_source()

        factory = ProbeDataSourceFactory(
            None,
            input_slots_size=1,
            output_slots_size=1,
            run_function=get_run_function(1))
        self.model_2 = factory.create_model()

        factory = ProbeMCOFactory(None)
        mco_model = factory.create_model()
        mco_model.parameters.append(ProbeParameter(None, name='P1'))
        mco_model.parameters.append(ProbeParameter(None, name='P2'))

        self.workflow = Workflow(
            mco=mco_model,
            execution_layers=[
                ExecutionLayer(
                    data_sources=[self.model_1, self.model_2]
                )
            ]
        )

        self.variable_names_registry = VariableNamesRegistry(
            workflow=self.workflow)

        self.data_source_mv_1 = DataSourceModelView(
            model=self.model_1,
            variable_names_registry=self.variable_names_registry
        )

    def test_evaluator_model_view_init(self):
        self.assertEqual(self.data_source_mv_1.label, "test_data_source")
        self.assertIsInstance(self.data_source_mv_1.model, BaseDataSourceModel)
        self.assertEqual(
            len(self.data_source_mv_1.input_slots_representation), 1)
        self.assertEqual(
            len(self.data_source_mv_1.output_slots_representation), 2)
        self.assertEqual(self.model_1.input_slot_info[0].name, '')
        self.assertEqual(self.model_1.output_slot_info[0].name, '')

    def test_input_slot_update(self):
        self.data_source_mv_1.input_slots_representation[0].name = 'P1'
        self.assertEqual(self.model_1.input_slot_info[0].name, 'P1')

        self.workflow.mco.parameters[0].name = 'P2'
        self.assertEqual(self.model_1.input_slot_info[0].name, '')

        self.data_source_mv_1.input_slots_representation[0].name = 'P2'
        self.assertEqual(self.model_1.input_slot_info[0].name, 'P2')

        with self.assertRaises(TraitError):
            self.data_source_mv_1.input_slots_representation[0].name = 'P1'

    def test_output_slot_update(self):
        self.data_source_mv_1.output_slots_representation[0].name = 'output'
        self.assertEqual(self.model_1.output_slot_info[0].name, 'output')

    def test_bad_input_slots(self):
        input_slots, _ = self.data_source.slots(self.model_1)

        self.model_1.input_slot_info = [
            InputSlotInfo(name='') for input_slot in range(
                len(input_slots) + 1)
        ]

        with self.assertRaisesRegexp(RuntimeError, "input slots"):
            DataSourceModelView(
                model=self.model_1,
                variable_names_registry=self.variable_names_registry)

    def test_bad_output_slots(self):
        _, output_slots = self.data_source.slots(self.model_1)

        self.model_1.output_slot_info = [
            OutputSlotInfo(name='')
            for slot in range(len(output_slots) + 1)]

        with self.assertRaisesRegexp(RuntimeError, "output slots"):
            DataSourceModelView(
                model=self.model_1,
                variable_names_registry=self.variable_names_registry)

    def test_update_table(self):
        self.model_1.output_slot_info[0].name = 'p1'
        self.model_1.output_slot_info[1].name = 't1'

        self.assertEqual(
            self.data_source_mv_1.output_slots_representation[0].name,
            'p1'
        )
        self.assertEqual(
            self.data_source_mv_1.output_slots_representation[1].name,
            't1'
        )

        self.model_1.input_slot_info[0].name = 'P2'
        self.assertEqual(
            self.data_source_mv_1.input_slots_representation[0].name,
            'P2'
        )
