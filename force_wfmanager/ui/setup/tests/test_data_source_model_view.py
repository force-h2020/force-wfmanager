import unittest

from traits.api import TraitError

from force_bdss.api import (DataValue, ExecutionLayer, OutputSlotInfo,
                            Workflow, InputSlotInfo, BaseDataSourceModel)
from force_bdss.tests.probe_classes.data_source import \
    ProbeDataSourceFactory
from force_bdss.tests.probe_classes.mco import ProbeMCOFactory, ProbeParameter
from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin

from force_wfmanager.ui.setup.data_source_model_view import \
    DataSourceModelView
from force_wfmanager.utils.variable_names_registry import \
    VariableNamesRegistry


def get_run_function(nb_outputs):
    def run(*args, **kwargs):
        return [DataValue() for _ in range(nb_outputs)]
    return run


class TestDataSourceModelView(unittest.TestCase):
    def setUp(self):
        self.plugin = ProbeExtensionPlugin()
        factory = ProbeDataSourceFactory(
            self.plugin,
            input_slots_size=1,
            output_slots_size=2,
            run_function=get_run_function(2))

        self.model_1 = factory.create_model()
        self.data_source = factory.create_data_source()

        factory = ProbeDataSourceFactory(
            self.plugin,
            input_slots_size=1,
            output_slots_size=1,
            run_function=get_run_function(1))
        self.model_2 = factory.create_model()

        factory = ProbeMCOFactory(self.plugin)
        mco_model = factory.create_model()
        mco_model.parameters.append(ProbeParameter(None, name='P1',
                                                   type='PRESSURE'))
        mco_model.parameters.append(ProbeParameter(None, name='P2',
                                                   type='PRESSURE'))

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
            InputSlotInfo(name='') for _ in range(len(input_slots) + 1)  # noqa
        ]

        with self.assertRaisesRegex(RuntimeError, "input slots"):
            DataSourceModelView(
                model=self.model_1,
                variable_names_registry=self.variable_names_registry)

    def test_bad_output_slots(self):
        _, output_slots = self.data_source.slots(self.model_1)

        self.model_1.output_slot_info = [
            OutputSlotInfo(name='')
            for slot in range(len(output_slots) + 1)]

        with self.assertRaisesRegex(RuntimeError, "output slots"):
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

    def test_HTML_description(self):
        self.assertIn("No Item Selected",
                      self.data_source_mv_1.selected_slot_description)
        out_slot = self.data_source_mv_1.output_slots_representation[0]
        self.data_source_mv_1.selected_slot_row = out_slot
        self.assertIn("Output row 0",
                      self.data_source_mv_1.selected_slot_description)
        self.assertIn("PRESSURE",
                      self.data_source_mv_1.selected_slot_description)
        in_slot = self.data_source_mv_1.input_slots_representation[0]
        self.data_source_mv_1.selected_slot_row = in_slot
        self.assertIn("Input row 0",
                      self.data_source_mv_1.selected_slot_description)
        self.assertIn("PRESSURE",
                      self.data_source_mv_1.selected_slot_description)
