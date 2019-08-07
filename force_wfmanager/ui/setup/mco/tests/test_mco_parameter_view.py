import unittest

from traits.testing.unittest_tools import UnittestTools

from force_wfmanager.ui.setup.mco.mco_parameter_view import \
    MCOParameterView
from force_wfmanager.utils.variable import Variable
from force_wfmanager.utils.tests.test_variable_names_registry import \
    get_basic_workflow


class TestMCOParameterView(unittest.TestCase, UnittestTools):

    def setUp(self):
        self.workflow = get_basic_workflow()
        self.param1 = self.workflow.mco.parameters[0]
        self.param2 = self.workflow.mco.parameters[1]
        self.param3 = self.workflow.mco.parameters[2]
        self.data_source1 = self.workflow.execution_layers[0].data_sources[0]
        self.data_source2 = self.workflow.execution_layers[0].data_sources[1]

        self.param1.name = 'T1'
        self.param1.type = 'PRESSURE'

        self.available_variables = [
            Variable(name='T1', type='PRESSURE'),
            Variable(name='T2', type='PRESSURE')
        ]

        self.parameter_view = MCOParameterView(
            model=self.workflow.mco,
            parameter_name_options=self.available_variables
        )

    def test_mco_parameter_view_init(self):

        self.assertEqual(3, len(self.parameter_view.model_views))
        self.assertEqual(
            "Probe parameter: PRESSURE T1",
            self.parameter_view.model_views[0].label,
        )
        self.assertEqual(
            "Probe parameter",
            self.parameter_view.model_views[1].label,
        )

        self.assertIsNotNone(self.parameter_view.parameter_entity_creator)
        self.assertEqual(
            self.parameter_view.selected_model_view,
            self.parameter_view.model_views[0]
        )
        self.assertEqual('MCO Parameters', self.parameter_view.label)
        self.assertEqual(
            self.available_variables[0],
            self.parameter_view.model_views[0].selected_variable,
        )
        self.assertEqual(
            self.available_variables[0].name,
            self.parameter_view.model_views[0].selected_variable.name
        )

    def test_parameter_entity_creator(self):

        mco_model = self.parameter_view.model
        self.parameter_view.model = None
        self.assertIsNone(self.parameter_view.parameter_entity_creator)
        self.assertEqual(0, len(self.parameter_view.model_views))
        self.assertEqual(None, self.parameter_view.selected_model_view)

        self.parameter_view.model = mco_model
        self.assertIsNotNone(self.parameter_view.parameter_entity_creator)

    def test_add_parameter(self):

        self.parameter_view.parameter_entity_creator.selected_factory = (
            self.parameter_view.parameter_entity_creator.factories[0]
        )

        parameter_model_view = self.parameter_view.model_views[2]
        self.parameter_view._add_parameter_button_fired()

        self.assertEqual(parameter_model_view,
                         self.parameter_view.model_views[2])
        self.assertEqual(4, len(self.workflow.mco.parameters))
        self.assertEqual(4, len(self.parameter_view.model_views))

        parameter_model_view = self.parameter_view.model_views[3]
        self.assertTrue(parameter_model_view.selected_variable.empty)
        self.assertEqual('', parameter_model_view.selected_variable.name)

        self.assertEqual(
            "Probe parameter",
            parameter_model_view.label,
        )
        self.assertEqual(
            self.parameter_view.selected_model_view,
            self.parameter_view.model_views[3]
        )

        self.parameter_view._dclick_add_parameter(None)
        self.assertEqual(5, len(self.workflow.mco.parameters))

    def test_remove_parameter(self):

        parameter_model_view = self.parameter_view.model_views[1]
        keep_model_view = self.parameter_view.model_views[0]
        self.parameter_view.selected_model_view = parameter_model_view
        self.parameter_view._remove_parameter_button_fired()

        self.assertEqual(2, len(self.workflow.mco.parameters))
        self.assertEqual(2, len(self.parameter_view.model_views))
        self.assertEqual(
            keep_model_view,
            self.parameter_view.model_views[0]
        )
        self.assertEqual(
            self.parameter_view.selected_model_view,
            self.parameter_view.model_views[0]
        )

        self.parameter_view._remove_parameter_button_fired()
        self.assertEqual(
            self.parameter_view.selected_model_view,
            self.parameter_view.model_views[0]
        )
        self.parameter_view._remove_parameter_button_fired()
        self.assertIsNone(self.parameter_view.selected_model_view)

    def test__parameter_names_check(self):

        self.parameter_view.model_views[0].selected_variable = (
            self.parameter_view.model_views[0].available_variables[1]
        )
        self.parameter_view.model_views[1].selected_variable = (
            self.parameter_view.model_views[1].available_variables[2]
        )

        error_message = self.parameter_view.verify()
        self.assertEqual(0, len(error_message))

        self.parameter_view.model_views[0].selected_variable = (
            self.parameter_view.model_views[0].available_variables[2]
        )
        error_message = self.parameter_view.verify()
        self.assertIn(
            'Two or more Parameters have a duplicate name',
            error_message[0].local_error,
        )

    def test_verify_workflow_event(self):

        parameter_model_view = self.parameter_view.model_views[0]
        with self.assertTraitChanges(
                self.parameter_view, 'verify_workflow_event', count=1):
            parameter_model_view.selected_variable = (
                self.available_variables[1]
            )
            self.assertEqual('T2', parameter_model_view.model.name)
        with self.assertTraitChanges(
                self.parameter_view, 'verify_workflow_event', count=0):
            parameter_model_view.model.name = 'another'
            self.assertEqual('T2', parameter_model_view.model.name)
