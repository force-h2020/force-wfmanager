from unittest import mock, TestCase

from force_bdss.api import (
    ExecutionLayer,
    Workflow,
    BaseMCOModel,
    KPISpecification,
    VerifierError,
    RangedMCOParameter,
    RangedMCOParameterFactory,
    RangedVectorMCOParameter,
    RangedVectorMCOParameterFactory,
)

from force_bdss.tests.dummy_classes.mco import DummyMCOFactory

from force_wfmanager.tests.dummy_classes.dummy_mco_options_view import (
    DummyBaseMCOOptionsView,
)
from force_wfmanager.ui.setup.system_state import SystemState
from force_wfmanager.ui.setup.tests.wfmanager_base_test_case import (
    WfManagerBaseTestCase,
)
from force_wfmanager.ui.setup.workflow_tree import (
    WorkflowTree,
    TreeNodeWithStatus,
    verifier_check,
)


class TestWorkflowTree(WfManagerBaseTestCase):
    def setUp(self):
        super(TestWorkflowTree, self).setUp()
        data_sources = [
            self.factory_registry.data_source_factories[2].create_model(),
            self.factory_registry.data_source_factories[3].create_model(),
        ]
        execution_layer = ExecutionLayer(data_sources=data_sources)
        self.workflow.execution_layers.append(execution_layer)
        self.workflow.mco_model.kpis.append(KPISpecification())

        self.system_state = SystemState()
        self.workflow_tree = WorkflowTree(
            model=self.workflow,
            _factory_registry=self.factory_registry,
            system_state=self.system_state,
        )

    def test_ui_initialization(self):

        self.assertEqual(1, len(self.workflow_tree.workflow_view.mco_view))
        self.assertEqual(1, len(self.workflow_tree.workflow_view.process_view))
        self.assertEqual(
            1, len(self.workflow_tree.workflow_view.communicator_view)
        )

        process_view = self.workflow_tree.workflow_view.process_view[0]

        self.assertEqual(
            2, len(self.workflow_tree.workflow_view.model.execution_layers)
        )
        self.assertEqual(2, len(process_view.execution_layer_views))
        self.assertEqual(
            2, len(process_view.model.execution_layers[0].data_sources)
        )
        self.assertEqual(
            2, len(process_view.execution_layer_views[0].data_source_views)
        )

        self.assertEqual(self.system_state, self.workflow_tree.system_state)

        self.assertIsNone(self.system_state.entity_creator)
        self.assertIsNone(self.system_state.add_new_entity)

    def test_workflow_selected(self):

        self.workflow_tree.workflow_selected(self.workflow_tree.workflow_view)
        self.assertEqual("Workflow", self.system_state.selected_factory_name)
        self.assertIsNone(self.system_state.add_new_entity)
        self.assertIsNone(self.system_state.remove_entity)
        self.assertIsNone(self.system_state.entity_creator)

    def test_process_selected(self):

        process_view = self.workflow_tree.workflow_view.process_view[0]
        self.workflow_tree.process_selected(process_view)
        self.assertEqual(
            "Execution Layer", self.system_state.selected_factory_name
        )
        self.assertIsNotNone(self.system_state.add_new_entity)
        self.assertIsNone(self.system_state.remove_entity)
        self.assertIsNone(self.system_state.entity_creator)

    def test_execution_layer_selected(self):
        execution_layer_view = self.workflow_tree.workflow_view.process_view[
            0
        ].execution_layer_views[0]
        self.workflow_tree.execution_layer_selected(execution_layer_view)
        self.assertEqual(
            "Data Source", self.system_state.selected_factory_name
        )
        self.assertIsNotNone(self.system_state.add_new_entity)
        self.assertIsNotNone(self.system_state.remove_entity)
        self.assertIsNotNone(self.system_state.entity_creator)

    def test_data_source_selected(self):
        data_source_view = (
            self.workflow_tree.workflow_view.process_view[0]
            .execution_layer_views[0]
            .data_source_views[0]
        )
        self.workflow_tree.data_source_selected(data_source_view)
        self.assertEqual("None", self.system_state.selected_factory_name)
        self.assertIsNone(self.system_state.add_new_entity)
        self.assertIsNotNone(self.system_state.remove_entity)
        self.assertIsNone(self.system_state.entity_creator)

    def test_mco_selected(self):
        mco_view = self.workflow_tree.workflow_view.mco_view[0]
        self.workflow_tree.mco_selected(mco_view)
        self.assertEqual("MCO", self.system_state.selected_factory_name)
        self.assertIsNotNone(self.system_state.add_new_entity)
        self.assertIsNone(self.system_state.remove_entity)
        self.assertIsNotNone(self.system_state.entity_creator)

    def test_mco_parameters_selected(self):
        mco_view = self.workflow_tree.workflow_view.mco_view[0]
        self.workflow_tree.mco_parameters_selected(mco_view)
        self.assertEqual(
            "MCO Parameters", self.system_state.selected_factory_name
        )

        self.assertIsNone(self.system_state.add_new_entity)
        self.assertIsNone(self.system_state.remove_entity)
        self.assertIsNone(self.system_state.entity_creator)

    def test_mco_kpis_selected(self):
        mco_view = self.workflow_tree.workflow_view.mco_view[0]
        self.workflow_tree.mco_kpis_selected(mco_view)
        self.assertEqual("MCO KPIs", self.system_state.selected_factory_name)

        self.assertIsNone(self.system_state.add_new_entity)
        self.assertIsNone(self.system_state.remove_entity)
        self.assertIsNone(self.system_state.entity_creator)

    def test_transfer_parameters(self):

        # create old model
        old_factory = DummyMCOFactory(plugin={'id': 'bcy356', 'name': 'old'})
        old_factory.parameter_factory_classes = [
            RangedVectorMCOParameterFactory,
            RangedMCOParameterFactory
        ]
        old_model = BaseMCOModel(factory=old_factory)
        old_model.parameters = [
            RangedMCOParameter(
                initial_value=1.0,
                factory=RangedVectorMCOParameterFactory(old_factory)
            ),
            RangedVectorMCOParameter(
                initial_value=[1.0, 1.0],
                factory=RangedMCOParameterFactory(old_factory)
            )
        ]
        old_model.kpis = []

        # create new model, that we want to transfer the parameters and
        # kpis to.
        new_factory = DummyMCOFactory(plugin={'id': 'xxui1', 'name': 'new'})
        new_factory.parameter_factory_classes = [
            RangedVectorMCOParameterFactory,
            RangedMCOParameterFactory
        ]
        new_model = BaseMCOModel(factory=new_factory)

        # workflow tree to work with
        workflow_tree = WorkflowTree(
            model=Workflow(),
            _factory_registry=self.factory_registry,
            system_state=self.system_state,
        )

        # transfer the parameters and kpis
        workflow_tree.transfer_parameters_and_kpis(old_model, new_model)

        # have two parameters been transferred?
        self.assertEqual(2, len(new_model.parameters))

        # has the correct plugin id been transferred?
        self.assertEqual(
            'xxui1',
            new_model.parameters[0].factory.mco_factory.plugin_id
        )

    def test_new_mco(self):

        workflow_no_mco = Workflow()
        workflow_tree = WorkflowTree(
            model=workflow_no_mco,
            _factory_registry=self.factory_registry,
            system_state=self.system_state,
        )

        self.assertIsNone(workflow_tree.workflow_view.model.mco_model)
        self.assertEqual(len(workflow_tree.workflow_view.mco_view), 0)

        workflow_tree.mco_selected(workflow_tree.workflow_view)

        mco_factory = self.factory_registry.mco_factories[0]
        self.system_state.entity_creator.model = mco_factory.create_model()
        self.system_state.add_new_entity()

        self.assertIsNotNone(workflow_tree.workflow_view.model.mco_model)
        self.assertEqual(len(workflow_tree.workflow_view.mco_view), 1)
        self.assertIsInstance(
            workflow_tree.workflow_view.model.mco_model, BaseMCOModel
        )

    def test_delete_mco(self):

        self.assertIsNotNone(self.workflow_tree.model.mco_model)
        self.assertEqual(1, len(self.workflow_tree.workflow_view.mco_view))

        mco_view = self.workflow_tree.workflow_view.mco_view[0]

        self.workflow_tree.mco_optimizer_selected(mco_view)
        self.system_state.remove_entity()

        self.assertIsNone(self.workflow_tree.model.mco_model)
        self.assertEqual(0, len(self.workflow_tree.workflow_view.mco_view))

    def test_new_execution_layer(self):

        process_view = self.workflow_tree.workflow_view.process_view[0]
        self.workflow_tree.process_selected(process_view)

        self.system_state.add_new_entity()

        self.assertEqual(3, len(process_view.execution_layer_views))

    def test_delete_execution_layer(self):
        process_view = self.workflow_tree.workflow_view.process_view[0]
        first_execution_layer = process_view.execution_layer_views[0]
        second_execution_layer = process_view.execution_layer_views[1]

        self.workflow_tree.execution_layer_selected(first_execution_layer)

        self.system_state.remove_entity()

        self.assertEqual(1, len(process_view.execution_layer_views))
        self.assertEqual(1, len(process_view.model.execution_layers))

        self.assertNotEqual(
            first_execution_layer, process_view.execution_layer_views[0]
        )
        self.assertEqual(
            len(second_execution_layer.data_source_views),
            len(process_view.execution_layer_views[0].data_source_views),
        )

    def test_new_data_source(self):
        process_view = self.workflow_tree.workflow_view.process_view[0]
        execution_layer = process_view.execution_layer_views[0]

        self.assertEqual(len(execution_layer.data_source_views), 2)

        self.workflow_tree.execution_layer_selected(execution_layer)

        data_factory = self.factory_registry.data_source_factories[0]
        self.system_state.entity_creator.model = data_factory.create_model()

        self.system_state.add_new_entity()

        self.assertEqual(len(execution_layer.data_source_views), 3)

    def test_delete_data_source(self):
        process_view = self.workflow_tree.workflow_view.process_view[0]
        data_source = process_view.execution_layer_views[0].data_source_views[
            0
        ]

        self.workflow_tree.data_source_selected(data_source)

        self.system_state.remove_entity()

        self.assertEqual(
            1, len(process_view.execution_layer_views[0].data_source_views)
        )
        self.assertEqual(
            1, len(process_view.model.execution_layers[0].data_sources)
        )

    def test_new_notification_listener(self):
        communicator_view = self.workflow_tree.workflow_view.communicator_view[
            0
        ]

        self.assertEqual(1, len(communicator_view.notification_listener_views))
        self.assertEqual(1, len(self.workflow.notification_listeners))

        self.workflow_tree.communicator_selected(communicator_view)
        factory = self.factory_registry.notification_listener_factories[0]
        self.system_state.entity_creator.model = factory.create_model()
        self.system_state.add_new_entity()

        self.assertIsNotNone(self.system_state.entity_creator)
        self.assertEqual(2, len(communicator_view.notification_listener_views))
        self.assertEqual(2, len(self.workflow.notification_listeners))

    def test_delete_notification_listener(self):
        communicator_view = self.workflow_tree.workflow_view.communicator_view[
            0
        ]
        self.assertEqual(1, len(communicator_view.notification_listener_views))
        self.assertEqual(1, len(self.workflow.notification_listeners))

        listener_view = communicator_view.notification_listener_views[0]
        self.workflow_tree.notification_listener_selected(listener_view)
        self.system_state.remove_entity()

        self.assertEqual(0, len(communicator_view.notification_listener_views))
        self.assertEqual(0, len(self.workflow.notification_listeners))

    def test_error_messaging(self):

        self.assertIsNone(self.system_state.selected_view)
        self.assertIn("No Item Selected", self.workflow_tree.selected_error)

        self.system_state.selected_view = self.workflow_tree.workflow_view
        self.assertIn(
            "An input slot is not named", self.workflow_tree.selected_error
        )

        data_source_view = (
            self.workflow_tree.workflow_view.process_view[0]
            .execution_layer_views[0]
            .data_source_views[0]
        )
        data_source_view.model.output_slot_info[0].name = "something"
        self.system_state.selected_view = data_source_view

        self.assertIn(
            "An output variable has an undefined name",
            self.workflow_tree.selected_error,
        )

    def test_mco_error_messaging_independence(self):

        mco_view = self.workflow_tree.workflow_view.mco_view[0]
        self.assertIn(
            "A KPI is not named",
            self.workflow_tree.workflow_view.error_message,
        )

        self.assertFalse(mco_view.kpi_view.model_views[0].valid)
        self.assertFalse(mco_view.kpi_view.valid)
        self.assertFalse(mco_view.valid)
        self.assertFalse(self.workflow_tree.workflow_view.valid)

        self.workflow.mco_model.kpis = []
        self.assertTrue(mco_view.parameter_view.valid)

        self.system_state.selected_view = mco_view.parameter_view
        self.assertIn("No errors", self.workflow_tree.selected_error)

        mco_view.parameter_view.model_views[0].model.name = ""
        self.assertIn(
            "An MCO parameter is not named", self.workflow_tree.selected_error
        )
        self.assertIn(
            "An MCO parameter has no type set",
            self.workflow_tree.selected_error,
        )
        self.assertFalse(mco_view.parameter_view.valid)


class TestProcessElementNode(TestCase):
    def test_wfelement_node(self):

        wfelement_node = TreeNodeWithStatus()
        obj = mock.Mock()
        obj.valid = True
        self.assertEqual(
            wfelement_node.get_icon(obj, False), "icons/valid.png"
        )
        obj.valid = False
        self.assertEqual(
            wfelement_node.get_icon(obj, False), "icons/invalid.png"
        )


class TestVerifierCheck(TestCase):
    def setUp(self):
        self.view = DummyBaseMCOOptionsView()
        self.verifier_error = VerifierError(
            subject=self.view,
            local_error="an error",
            global_error="AN ERROR",
            severity="error",
        )
        self.message_list = []
        self.send_to_parent = []

    def test_verifier_check_error(self):

        self.assertTrue(self.view.valid)
        self.assertEqual(0, len(self.message_list))
        self.assertEqual(0, len(self.send_to_parent))

        verifier_check(
            self.verifier_error,
            "error",
            self.message_list,
            self.send_to_parent,
            self.view,
        )

        self.assertFalse(self.view.valid)
        self.assertEqual(1, len(self.message_list))
        self.assertEqual("an error", self.message_list[0])
        self.assertEqual(1, len(self.send_to_parent))
        self.assertEqual("AN ERROR", self.send_to_parent[0])

    def test_verifier_check_warning(self):

        self.verifier_error.severity = "warning"
        self.verifier_error.local_error = "a warning"
        self.verifier_error.global_error = "A WARNING"

        self.assertTrue(self.view.valid)
        self.assertEqual(0, len(self.message_list))
        self.assertEqual(0, len(self.send_to_parent))

        verifier_check(
            self.verifier_error,
            "error",
            self.message_list,
            self.send_to_parent,
            self.view,
        )

        self.assertTrue(self.view.valid)
        self.assertEqual(1, len(self.message_list))
        self.assertEqual("a warning", self.message_list[0])
        self.assertEqual(0, len(self.send_to_parent))

        verifier_check(
            self.verifier_error,
            "warning",
            self.message_list,
            self.send_to_parent,
            self.view,
        )

        self.assertFalse(self.view.valid)
        self.assertEqual(1, len(self.message_list))
        self.assertEqual("a warning", self.message_list[0])
        self.assertEqual(1, len(self.send_to_parent))
        self.assertEqual("A WARNING", self.send_to_parent[0])
