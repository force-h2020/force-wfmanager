from force_bdss.api import (OutputSlotInfo, InputSlotInfo, BaseDataSourceModel)

from force_wfmanager.ui.setup.process.data_source_view import \
    DataSourceView
from force_wfmanager.ui.setup.tests.wfmanager_base_test_case import (
    WfManagerBaseTestCase
)


class TestDataSourceView(WfManagerBaseTestCase):

    def setUp(self):
        super(TestDataSourceView, self).setUp()
        factory = self.factory_registry.data_source_factories[1]
        self.data_source = factory.create_data_source()
        self.data_source_view = DataSourceView(
            model=self.model_1,
            variable_names_registry=self.variable_names_registry
        )

    def test_init_data_source_view(self):
        self.assertEqual(
            2,
            len(self.data_source_view.output_slots_representation))
        self.assertEqual(
            len(self.data_source_view.output_slots_representation),
            len(self.model_1.output_slot_info))

    def test_evaluator_view_init(self):
        self.assertEqual("test_data_source", self.data_source_view.label)
        self.assertIsInstance(self.data_source_view.model, BaseDataSourceModel)
        self.assertEqual(
            1, len(self.data_source_view.input_slots_representation))
        self.assertEqual(
            2, len(self.data_source_view.output_slots_representation))
        self.assertEqual('P1', self.model_1.input_slot_info[0].name)
        self.assertEqual('', self.model_1.output_slot_info[0].name)

    def test_input_slot_update(self):
        self.workflow.mco.parameters[0].name = 'P2'
        self.assertEqual('P1', self.model_1.input_slot_info[0].name)

        self.data_source_view.input_slots_representation[0].model.name = 'P2'
        self.assertEqual('P2', self.model_1.input_slot_info[0].name)

    def test_output_slot_update(self):
        self.data_source_view.output_slots_representation[0].model.name = 'output'
        self.assertEqual('output', self.model_1.output_slot_info[0].name)

    def test_bad_input_slots(self):
        input_slots, _ = self.data_source.slots(self.model_1)

        self.model_1.input_slot_info = [
            InputSlotInfo(name='') for _ in range(len(input_slots) + 1) # noqa
        ]

        with self.assertRaisesRegex(RuntimeError, "input slots"):
            DataSourceView(
                model=self.model_1,
                variable_names_registry=self.variable_names_registry)

    def test_bad_output_slots(self):
        _, output_slots = self.data_source.slots(self.model_1)

        self.model_1.output_slot_info = [
            OutputSlotInfo(name='')
            for slot in range(len(output_slots) + 1)]

        with self.assertRaisesRegex(RuntimeError, "output slots"):
            DataSourceView(
                model=self.model_1,
                variable_names_registry=self.variable_names_registry)

    def test_update_table(self):
        self.model_1.output_slot_info[0].name = 'p1'
        self.model_1.output_slot_info[1].name = 't1'

        self.assertEqual(
            'p1',
            self.data_source_view.output_slots_representation[0].model.name
        )
        self.assertEqual(
            't1',
            self.data_source_view.output_slots_representation[1].model.name
        )

        self.model_1.input_slot_info[0].name = 'P2'
        self.assertEqual(
            'P2',
            self.data_source_view.input_slots_representation[0].model.name
        )

    def test_HTML_description(self):
        self.assertIn("No Item Selected",
                      self.data_source_view.selected_slot_description)
        out_slot = self.data_source_view.output_slots_representation[0]
        self.data_source_view.selected_slot_row = out_slot
        self.assertIn("Output row 0",
                      self.data_source_view.selected_slot_description)
        self.assertIn("PRESSURE",
                      self.data_source_view.selected_slot_description)
        in_slot = self.data_source_view.input_slots_representation[0]
        self.data_source_view.selected_slot_row = in_slot
        self.assertIn("Input row 0",
                      self.data_source_view.selected_slot_description)
        self.assertIn("PRESSURE",
                      self.data_source_view.selected_slot_description)
