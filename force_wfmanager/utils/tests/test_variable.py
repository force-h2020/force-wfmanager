import unittest

from force_bdss.api import OutputSlotInfo, InputSlotInfo
from force_bdss.tests.probe_classes.data_source import (
    ProbeDataSourceFactory
)

from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin

from force_wfmanager.ui.setup.process.data_source_view import (
    DataSourceView, InputSlotRow
)
from force_wfmanager.utils.variable import (
    Variable
)


class VariableTest(unittest.TestCase):

    def setUp(self):
        plugin = ProbeExtensionPlugin()
        self.data_source_factory = ProbeDataSourceFactory(
            plugin,
            input_slots_size=1,
            output_slots_size=1)

        data_source = self.data_source_factory.create_model()
        data_source.output_slot_info = [OutputSlotInfo(name='T1')]

        data_source_view = DataSourceView(model=data_source)
        output_row = data_source_view.output_slots_representation[0]

        self.variable = Variable(
            origin=data_source_view,
            output_slot_row=output_row,
        )

    def test___init___(self):

        self.assertIsNotNone(self.variable.output_slot_info)
        self.assertFalse(self.variable.empty)
        self.assertEqual('T1', self.variable.name)
        self.assertEqual('PRESSURE', self.variable.type)
        self.assertEqual('PRESSURE T1', self.variable.label)

    def test_label(self):
        self.variable.name = 'P1'
        self.assertEqual('PRESSURE T1', self.variable.label)
        self.variable.output_slot_info.name = 'P1'
        self.assertEqual('PRESSURE P1', self.variable.label)

    def test_empty(self):
        self.variable.output_slot_row = None
        self.assertTrue(self.variable.empty)
        self.variable.input_slot_rows.append((1, InputSlotRow()))
        self.assertFalse(self.variable.empty)

    def test_reset_variable(self):
        input_row = InputSlotRow(model=InputSlotInfo(name='T1'))
        self.variable.input_slot_rows.append((1, input_row))
        self.variable.reset_variable()
        self.assertTrue(self.variable.empty)
        self.assertEqual('T1', input_row.model.name)

    def test_verify(self):
        errors = self.variable.verify()
        self.assertEqual(0, len(errors))

        self.variable.input_slot_rows.append((1, InputSlotRow()))

        errors = self.variable.verify()
        self.assertEqual(0, len(errors))

        self.variable.input_slot_rows.append((0, InputSlotRow()))

        errors = self.variable.verify()
        self.assertEqual(1, len(errors))
        self.assertIn(
            'Variable is being used as an input before being generated',
            errors[0].local_error)

    def test_update_name(self):
        input_row = InputSlotRow(model=InputSlotInfo(name='T1'))
        self.variable.input_slot_rows.append((1, input_row))

        self.variable.output_slot_info.name = 'V1'
        self.assertEqual('V1', self.variable.input_slot_rows[0][1].model.name)

        self.variable.output_slot_info.name = ''

        self.assertIsNone(self.variable.origin)
        self.assertIsNone(self.variable.output_slot_info)
        self.assertEqual(0, len(self.variable.input_slot_rows))
        self.assertTrue(self.variable.empty)

        self.assertEqual('V1', input_row.model.name)

    def test_check_input_slot_hook(self):
        input_slot = InputSlotRow(
            model=InputSlotInfo(name='T1'),
            type='PRESSURE'
        )
        self.assertTrue(self.variable.check_input_slot_hook(
            0, input_slot)
        )

        input_slot = InputSlotRow(
            model=InputSlotInfo(name='C1'),
            type='PRESSURE'
        )
        self.assertFalse(self.variable.check_input_slot_hook(
            0, input_slot)
        )
        self.assertEqual(1, len(self.variable.input_slot_rows))
