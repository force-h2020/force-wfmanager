import unittest
import mock

from force_bdss.api import (
    BaseMCOModel, Workflow, BaseNotificationListenerFactory, ExecutionLayer,
    KPISpecification
)

from force_bdss.tests.probe_classes.factory_registry_plugin import (
    ProbeFactoryRegistryPlugin
)


from force_wfmanager.left_side_pane.workflow_tree import (
    WorkflowTree, TreeNodeWithStatus, ModelEditDialog
)
from force_wfmanager.left_side_pane.new_entity_modal import NewEntityModal


NEW_ENTITY_MODAL_PATH = (
    "force_wfmanager.left_side_pane.workflow_tree.NewEntityModal"
)
MODEL_EDIT_PATH = (
    "force_wfmanager.left_side_pane.workflow_tree.ModelEditDialog"
)


def mock_new_modal(model_type, factory=None):
    def _mock_new_modal(*args, **kwargs):
        modal = mock.Mock(spec=NewEntityModal)
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


def mock_model_edit_dialog():
    model_edit_dialog = mock.Mock(spec=ModelEditDialog)
    model_edit_dialog.edit_traits = lambda: None
    return model_edit_dialog


def get_workflow_tree():
    factory_registry = ProbeFactoryRegistryPlugin()
    mco_factory = factory_registry.mco_factories[0]
    mco = mco_factory.create_model()
    parameter_factory = mco_factory.parameter_factories[0]
    mco.parameters.append(parameter_factory.create_model())
    mco.kpis.append(KPISpecification())
    data_source_factory = factory_registry.data_source_factories[0]
    notification_listener_factory = \
        factory_registry.notification_listener_factories[0]

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
                        data_source_factory.create_model()
                    ],
                )
            ]
        )
    )


class TestWorkflowTree(unittest.TestCase):
    def setUp(self):
        self.tree = get_workflow_tree()
        self.factory_registry = ProbeFactoryRegistryPlugin()

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

        self.tree.mco_factory_selected(self.tree.workflow_mv)
        self.tree.current_modal.model = \
            self.factory_registry.mco_factories[0].create_model()
        self.tree.add_new_entity()

        self.assertEqual(len(self.tree.workflow_mv.mco_mv), 1)
        self.assertIsInstance(self.tree.workflow_mv.model.mco, BaseMCOModel)

    def test_new_mco_parameter(self):

        self.assertEqual(
            len(self.tree.workflow_mv.mco_mv[0].mco_parameters_mv), 1)
        self.assertEqual(len(self.tree.workflow_mv.model.mco.parameters), 1)

        self.tree.parameter_factory_selected(self.tree.workflow_mv.mco_mv[0])

        parameter_factory = \
            self.factory_registry.mco_factories[0].parameter_factories[0]
        self.tree.current_modal.model = parameter_factory.create_model()
        self.tree.add_new_entity()

        self.assertEqual(
            len(self.tree.workflow_mv.mco_mv[0].mco_parameters_mv), 2)
        self.assertEqual(len(self.tree.workflow_mv.model.mco.parameters), 2)

    def test_new_data_source(self):

        exec_layer = self.tree.workflow_mv.execution_layers_mv[0]
        self.assertEqual(len(exec_layer.data_sources_mv), 2)
        self.assertEqual(
            len(self.tree.workflow_mv.model.execution_layers[0].data_sources),
            2
        )

        self.tree.datasource_factory_exec_instance_selected(exec_layer)
        self.tree.current_modal.model = \
            self.factory_registry.data_source_factories[0].create_model()
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

        self.tree.notification_factory_selected(self.tree.workflow_mv)
        nf_factory = self.factory_registry.notification_listener_factories[0]
        self.tree.current_modal.model = nf_factory.create_model()
        self.tree.add_new_entity()

        self.assertEqual(
            len(self.tree.workflow_mv.notification_listeners_mv), 2)
        self.assertEqual(
            len(self.tree.workflow_mv.model.notification_listeners), 2)

    def test_new_kpi(self):
        self.assertEqual(len(self.tree.workflow_mv.mco_mv[0].kpis_mv), 1)
        self.assertEqual(len(self.tree.workflow_mv.model.mco.kpis), 1)

        self.tree.kpi_factory_selected(self.tree.workflow_mv.mco_mv[0])
        self.tree.add_new_entity()

        self.assertEqual(len(self.tree.workflow_mv.mco_mv[0].kpis_mv), 2)
        self.assertEqual(len(self.tree.workflow_mv.model.mco.kpis), 2)

    def test_new_execution_layer(self):
        self.assertEqual(len(self.tree.workflow_mv.execution_layers_mv), 2)
        self.assertEqual(len(self.tree.workflow_mv.model.execution_layers), 2)

        self.tree.execution_layer_factory_selected(self.tree.workflow_mv)
        self.tree.add_new_entity()

        self.assertEqual(len(self.tree.workflow_mv.execution_layers_mv), 3)
        self.assertEqual(len(self.tree.workflow_mv.model.execution_layers), 3)

    def test_delete_notification_listener(self):
        self.assertEqual(
            len(self.tree.workflow_mv.notification_listeners_mv), 1)
        self.assertEqual(
            len(self.tree.workflow_mv.model.notification_listeners), 1)
        notif_instance = self.tree.workflow_mv.notification_listeners_mv[0]
        self.tree.notification_instance_selected(notif_instance)
        self.tree.remove_entity()

        self.assertEqual(
            len(self.tree.workflow_mv.notification_listeners_mv), 0)
        self.assertEqual(
            len(self.tree.workflow_mv.model.notification_listeners), 0)

    def test_delete_mco(self):
        self.assertIsNotNone(self.tree.model.mco)
        self.assertEqual(len(self.tree.workflow_mv.mco_mv), 1)

        self.tree.mco_instance_selected(self.tree.workflow_mv.mco_mv[0])
        self.tree.remove_entity()

        self.assertIsNone(self.tree.model.mco)
        self.assertEqual(len(self.tree.workflow_mv.mco_mv), 0)

    def test_delete_mco_parameter(self):
        self.assertEqual(len(self.tree.model.mco.parameters), 1)

        self.tree.parameter_instance_selected(
            self.tree.workflow_mv.mco_mv[0].mco_parameters_mv[0]
        )
        self.tree.remove_entity()

        self.assertEqual(len(self.tree.model.mco.parameters), 0)

    def test_delete_execution_layer(self):
        first_execution_layer = self.tree.workflow_mv.execution_layers_mv[0]
        self.assertEqual(len(self.tree.workflow_mv.execution_layers_mv), 2)
        self.assertEqual(len(self.tree.workflow_mv.model.execution_layers), 2)

        self.tree.datasource_factory_exec_instance_selected(
            first_execution_layer
        )
        self.tree.remove_entity()

        self.assertEqual(len(self.tree.workflow_mv.execution_layers_mv), 1)
        self.assertEqual(len(self.tree.workflow_mv.model.execution_layers), 1)

    def test_delete_kpi(self):
        self.assertEqual(len(self.tree.workflow_mv.mco_mv[0].kpis_mv), 1)
        self.assertEqual(len(self.tree.workflow_mv.model.mco.kpis), 1)

        self.tree.kpi_instance_selected(
            self.tree.workflow_mv.mco_mv[0].kpis_mv[0]
        )
        self.tree.remove_entity()

        self.assertEqual(len(self.tree.workflow_mv.mco_mv[0].kpis_mv), 0)
        self.assertEqual(len(self.tree.workflow_mv.model.mco.kpis), 0)

    def test_delete_datasource(self):
        data_source = \
            self.tree.workflow_mv.execution_layers_mv[0].data_sources_mv[0]
        self.assertEqual(
            len(self.tree.workflow_mv.execution_layers_mv[0].data_sources_mv),
            2)
        self.assertEqual(
            len(self.tree.workflow_mv.model.execution_layers[0].data_sources),
            2)

        self.tree.datasource_instance_selected(data_source)
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

        self.assertIn("An output parameter is undefined",
                      self.tree.selected_error)
        param_mv = self.tree.workflow_mv.mco_mv[0].mco_parameters_mv[0]
        self.tree.selected_mv = param_mv

        param_mv.model.name = 'P1'
        param_mv.model.type = 'PRESSURE'
        self.assertIn("No Errors", self.tree.selected_error)

    def test_error_scrolling(self):
        self.assertIsNone(self.tree.selected_mv)
        self.assertIn("No Item Selected", self.tree.selected_error)
        self.tree.selected_mv = self.tree.workflow_mv
        self.assertIn("An output parameter is undefined",
                      self.tree.selected_error)
        self.tree.next_error_btn = True
        self.assertIn("An input parameter is undefined",
                      self.tree.selected_error)
        self.tree.prev_error_btn = True
        self.assertIn("An output parameter is undefined",
                      self.tree.selected_error)
        self.tree.last_error_btn = True
        self.assertIn("Error in MCO", self.tree.selected_error)
        self.tree.first_error_btn = True
        self.assertIn("An output parameter is undefined",
                      self.tree.selected_error)

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
