import unittest
from unittest import mock

from force_bdss.api import (
    BaseMCOModel, Workflow, BaseNotificationListenerFactory, ExecutionLayer,
    KPISpecification
)

from force_bdss.tests.probe_classes.factory_registry import (
    ProbeFactoryRegistry, ProbeDataSourceFactory, ProbeExtensionPlugin
)


from force_wfmanager.models.workflow_tree import (
    WorkflowTree, TreeNodeWithStatus
)
from force_wfmanager.models.new_entity_creator import NewEntityCreator


NEW_ENTITY_MODAL_PATH = (
    "force_wfmanager.models.workflow_tree.NewEntityModal"
)


def mock_new_modal(model_type, factory=None):
    def _mock_new_modal(*args, **kwargs):
        modal = mock.Mock(spec=NewEntityCreator)
        modal.edit_traits = lambda: None

        # Any type is ok as long as it passes trait validation.
        # We choose BaseDataSourceModel.
        modal.current_model = model_type(factory=factory)
        return modal

    return _mock_new_modal


def mock_notification_listener_factory():
    mock_factory = mock.Mock(spec=BaseNotificationListenerFactory)
    mock_factory.ui_visible = True
    return mock_factory


def get_workflow_tree():
    factory_registry = ProbeFactoryRegistry()
    mco_factory = factory_registry.mco_factories[0]
    mco = mco_factory.create_model()
    parameter_factory = mco_factory.parameter_factories[0]
    mco.parameters.append(parameter_factory.create_model())
    mco.kpis.append(KPISpecification())
    data_source_factory = factory_registry.data_source_factories[0]
    notification_listener_factory = (
        factory_registry.notification_listener_factories[0]
    )
    data_source_factory_multi = ProbeDataSourceFactory(
        ProbeExtensionPlugin(),
        input_slots_size=2, output_slots_size=3
    )
    return WorkflowTree(
        _factory_registry=factory_registry,
        model=Workflow(
            mco=mco,
            notification_listeners=[
                notification_listener_factory.create_model(),
            ],
            execution_layers=[
                ExecutionLayer(
                    data_sources=[
                        data_source_factory.create_model(),
                        data_source_factory.create_model()
                    ],
                ),
                ExecutionLayer(
                    data_sources=[
                        data_source_factory.create_model(),
                        data_source_factory_multi.create_model()
                    ],
                )
            ]
        )
    )


class TestWorkflowTree(unittest.TestCase):
    def setUp(self):
        self.tree = get_workflow_tree()
        self.factory_registry = ProbeFactoryRegistry()

    def test_ui_initialization(self):
        self.assertIsNotNone(self.tree.model.mco)
        self.assertEqual(len(self.tree.model.execution_layers), 2)
        self.assertEqual(len(self.tree.workflow_mv.mco_mv), 1)
        self.assertEqual(len(self.tree.workflow_mv.execution_layers_mv), 2)

    def test_new_mco(self):

        self.tree = WorkflowTree(model=Workflow(),
                                 _factory_registry=self.factory_registry)
        self.assertIsNone(self.tree.workflow_mv.model.mco)
        self.assertEqual(len(self.tree.workflow_mv.mco_mv), 0)

        self.tree.factory(
            self.factory_registry.mco_factories,
            self.tree.new_mco,
            'MCO',
            self.tree.workflow_mv
        )
        self.tree.entity_creator.model = (
            self.factory_registry.mco_factories[0].create_model()
        )
        self.tree.add_new_entity()

        self.assertEqual(len(self.tree.workflow_mv.mco_mv), 1)
        self.assertIsInstance(self.tree.workflow_mv.model.mco, BaseMCOModel)

    def test_new_mco_parameter(self):

        self.assertEqual(
            len(self.tree.workflow_mv.mco_mv[0].mco_parameters_mv), 1)
        self.assertEqual(len(self.tree.workflow_mv.model.mco.parameters), 1)

        parameter_factory = (
            self.factory_registry.mco_factories[0].parameter_factories[0]
        )
        self.tree.factory(
            self.factory_registry.mco_factories[0].parameter_factories,
            self.tree.new_parameter,
            'Parameter',
            self.tree.workflow_mv.mco_mv[0]
        )
        self.tree.entity_creator.model = parameter_factory.create_model()
        self.tree.add_new_entity()
        self.assertEqual(
            len(self.tree.workflow_mv.mco_mv[0].mco_parameters_mv), 2
        )
        self.assertEqual(len(self.tree.workflow_mv.model.mco.parameters), 2)

    def test_new_data_source(self):

        exec_layer = self.tree.workflow_mv.execution_layers_mv[0]
        self.assertEqual(len(exec_layer.data_sources_mv), 2)
        self.assertEqual(
            len(self.tree.workflow_mv.model.execution_layers[0].data_sources),
            2
        )

        self.tree.factory_instance(
            self.factory_registry.data_source_factories,
            self.tree.new_data_source,
            'ExecutionLayer',
            self.tree.delete_layer,
            exec_layer
        )
        self.tree.entity_creator.model = (
            self.factory_registry.data_source_factories[0].create_model()
        )
        self.tree.add_new_entity()

        self.assertEqual(len(exec_layer.data_sources_mv), 3)
        self.assertEqual(
            len(self.tree.workflow_mv.model.execution_layers[0].data_sources),
            3
        )

    def test_new_notification_listener(self):
        self.assertEqual(
            len(self.tree.workflow_mv.notification_listeners_mv), 1)
        self.assertEqual(
            len(self.tree.workflow_mv.model.notification_listeners), 1)
        self.tree.factory(
            self.factory_registry.notification_listener_factories,
            self.tree.new_notification_listener,
            'NotificationListener',
            self.tree.workflow_mv
        )

        nf_factory = self.factory_registry.notification_listener_factories[0]
        self.tree.entity_creator.model = nf_factory.create_model()
        self.tree.add_new_entity()

        self.assertEqual(
            len(self.tree.workflow_mv.notification_listeners_mv), 2)
        self.assertEqual(
            len(self.tree.workflow_mv.model.notification_listeners), 2)

    def test_new_kpi(self):
        self.assertEqual(len(self.tree.workflow_mv.mco_mv[0].kpis_mv), 1)
        self.assertEqual(len(self.tree.workflow_mv.model.mco.kpis), 1)

        self.tree.factory(
            None,
            self.tree.new_kpi,
            'KPI',
            self.tree.workflow_mv.mco_mv[0]
        )
        self.tree.add_new_entity()

        self.assertEqual(len(self.tree.workflow_mv.mco_mv[0].kpis_mv), 2)
        self.assertEqual(len(self.tree.workflow_mv.model.mco.kpis), 2)

    def test_new_execution_layer(self):
        self.assertEqual(len(self.tree.workflow_mv.execution_layers_mv), 2)
        self.assertEqual(len(self.tree.workflow_mv.model.execution_layers), 2)

        self.tree.factory(
            None,
            self.tree.new_layer,
            'ExecutionLayer',
            self.tree.workflow_mv
        )
        self.tree.add_new_entity()

        self.assertEqual(len(self.tree.workflow_mv.execution_layers_mv), 3)
        self.assertEqual(len(self.tree.workflow_mv.model.execution_layers), 3)

    def test_delete_notification_listener(self):
        self.assertEqual(
            len(self.tree.workflow_mv.notification_listeners_mv), 1)
        self.assertEqual(
            len(self.tree.workflow_mv.model.notification_listeners), 1)
        notif_instance = self.tree.workflow_mv.notification_listeners_mv[0]
        self.tree.instance(
            self.tree.delete_notification_listener, notif_instance
        )
        self.tree.remove_entity()

        self.assertEqual(
            len(self.tree.workflow_mv.notification_listeners_mv), 0)
        self.assertEqual(
            len(self.tree.workflow_mv.model.notification_listeners), 0)

    def test_delete_mco(self):
        self.assertIsNotNone(self.tree.model.mco)
        self.assertEqual(len(self.tree.workflow_mv.mco_mv), 1)

        self.tree.instance(self.tree.delete_mco, self.tree.workflow_mv.mco_mv)
        self.tree.remove_entity()

        self.assertIsNone(self.tree.model.mco)
        self.assertEqual(len(self.tree.workflow_mv.mco_mv), 0)

    def test_delete_mco_parameter(self):
        self.assertEqual(len(self.tree.model.mco.parameters), 1)

        self.tree.instance(
            self.tree.delete_parameter,
            self.tree.workflow_mv.mco_mv[0].mco_parameters_mv[0]
        )
        self.tree.remove_entity()

        self.assertEqual(len(self.tree.model.mco.parameters), 0)

    def test_delete_execution_layer(self):
        first_execution_layer = self.tree.workflow_mv.execution_layers_mv[0]
        self.assertEqual(len(self.tree.workflow_mv.execution_layers_mv), 2)
        self.assertEqual(len(self.tree.workflow_mv.model.execution_layers), 2)

        self.tree.factory_instance(
            self.factory_registry.data_source_factories,
            self.tree.new_data_source,
            'ExecutionLayer',
            self.tree.delete_layer,
            first_execution_layer
        )
        self.tree.remove_entity()

        self.assertEqual(len(self.tree.workflow_mv.execution_layers_mv), 1)
        self.assertEqual(len(self.tree.workflow_mv.model.execution_layers), 1)

    def test_delete_kpi(self):
        self.assertEqual(len(self.tree.workflow_mv.mco_mv[0].kpis_mv), 1)
        self.assertEqual(len(self.tree.workflow_mv.model.mco.kpis), 1)

        self.tree.instance(
            self.tree.delete_kpi,
            self.tree.workflow_mv.mco_mv[0].kpis_mv[0]
        )
        self.tree.remove_entity()

        self.assertEqual(len(self.tree.workflow_mv.mco_mv[0].kpis_mv), 0)
        self.assertEqual(len(self.tree.workflow_mv.model.mco.kpis), 0)

    def test_delete_datasource(self):
        data_source = (
            self.tree.workflow_mv.execution_layers_mv[0].data_sources_mv[0]
        )
        self.assertEqual(
            len(self.tree.workflow_mv.execution_layers_mv[0].data_sources_mv),
            2)
        self.assertEqual(
            len(self.tree.workflow_mv.model.execution_layers[0].data_sources),
            2)

        self.tree.instance(self.tree.delete_data_source, data_source)
        self.tree.remove_entity()

        self.assertEqual(
            len(self.tree.workflow_mv.execution_layers_mv[0].data_sources_mv),
            1)
        self.assertEqual(
            len(self.tree.workflow_mv.model.execution_layers[0].data_sources),
            1)

    def test_error_messaging(self):
        self.assertIsNone(self.tree.selected_mv)
        self.assertIn("No Item Selected", self.tree.selected_error)
        self.tree.selected_mv = self.tree.workflow_mv

        self.assertIn(
            "An input slot is not named", self.tree.selected_error
        )
        param_mv = self.tree.workflow_mv.mco_mv[0].mco_parameters_mv[0]
        self.tree.selected_mv = param_mv

        param_mv.model.name = 'P1'
        param_mv.model.type = 'PRESSURE'
        self.assertIn("No errors", self.tree.selected_error)

        ds_mv = self.tree.workflow_mv.execution_layers_mv[1].data_sources_mv[1]
        ds_mv.model.output_slot_info[0].name = 'something'
        self.tree.selected_mv = ds_mv
        self.assertIn(
            "An output variable has an undefined name",
            self.tree.selected_error
        )


class TestWorkflowElementNode(unittest.TestCase):
    def test_wfelement_node(self):
        wfelement_node = TreeNodeWithStatus()
        obj = mock.Mock()
        obj.valid = True
        self.assertEqual(wfelement_node.get_icon(obj, False),
                         'icons/valid.png')
        obj.valid = False
        self.assertEqual(wfelement_node.get_icon(obj, False),
                         'icons/invalid.png')
