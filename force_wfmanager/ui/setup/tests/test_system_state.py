import unittest

from force_wfmanager.ui.setup.system_state import SystemState


class TestSystemState(unittest.TestCase):

    def setUp(self):
        self.system_state = SystemState()

    def test_system_state_init(self):
        self.assertIsNone(self.system_state.selected_view)
        self.assertEqual('None', self.system_state.selected_factory_name)
        self.assertIsNone(self.system_state.entity_creator)
        self.assertIsNone(self.system_state.add_new_entity)
        self.assertIsNone(self.system_state.remove_entity)
