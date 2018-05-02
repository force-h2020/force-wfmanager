import unittest

from force_bdss.core.execution_layer import ExecutionLayer
from force_bdss.data_sources.base_data_source_model import BaseDataSourceModel
from force_bdss.mco.base_mco_model import BaseMCOModel
from force_bdss.tests.probe_classes.factory_registry_plugin import \
    ProbeFactoryRegistryPlugin

try:
    import mock
except ImportError:
    from unittest import mock

from force_bdss.core.workflow import Workflow

from force_wfmanager.left_side_pane.workflow_tree import (
    WorkflowTree, TreeNodeWithStatus)
from force_wfmanager.left_side_pane.new_entity_modal import NewEntityModal


NEW_ENTITY_MODAL_PATH = \
    "force_wfmanager.left_side_pane.workflow_tree.NewEntityModal"


def mock_new_modal(model_type):
    def _mock_new_modal(*args, **kwargs):
        modal = mock.Mock(spec=NewEntityModal)
        modal.edit_traits = lambda: None

        # Any type is ok as long as it passes trait validation.
        # We choose BaseDataSourceModel.
        modal.current_model = model_type(factory=None)
        return modal

    return _mock_new_modal


def get_workflow_tree():
    factory_registry = ProbeFactoryRegistryPlugin()
    mco_factory = factory_registry.mco_factories[0]
    mco = mco_factory.create_model()
    parameter_factory = mco_factory.parameter_factories()[0]
    mco.parameters.append(parameter_factory.create_model())
    data_source_factory = factory_registry.data_source_factories[0]

    return WorkflowTree(
        factory_registry=factory_registry,
        model=Workflow(
            mco=mco,
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

    def test_ui_initialization(self):
        self.assertIsNotNone(self.tree.model.mco)
        self.assertEqual(len(self.tree.model.execution_layers), 2)
        self.assertEqual(len(self.tree.workflow_mv.mco_mv), 1)
        self.assertEqual(len(self.tree.workflow_mv.execution_layers_mv), 2)

    def test_new_mco(self):
        with mock.patch(NEW_ENTITY_MODAL_PATH) as mock_modal:
            mock_modal.side_effect = mock_new_modal(BaseMCOModel)
            mock_ui_info = mock.Mock()
            mock_object = mock.Mock()

            self.tree.new_mco(mock_ui_info, mock_object)

            mock_modal.assert_called()

    def test_new_mco_parameter(self):
        with mock.patch(NEW_ENTITY_MODAL_PATH) as mock_modal:
            mock_modal.side_effect = mock_new_modal(BaseMCOModel)
            mock_ui_info = mock.Mock()
            mock_object = mock.Mock()

            self.tree.new_parameter(mock_ui_info, mock_object)

            mock_modal.assert_called()
            mock_object.add_parameter.assert_called()

    def test_new_data_source(self):
        with mock.patch(NEW_ENTITY_MODAL_PATH) as mock_modal:
            mock_modal.side_effect = mock_new_modal(BaseDataSourceModel)
            mock_ui_info = mock.Mock()
            mock_object = mock.Mock()

            self.tree.new_data_source(mock_ui_info, mock_object)

            mock_modal.assert_called()
            mock_object.add_data_source.assert_called()

    def test_edit_entity(self):
        mock_ui_info = mock.Mock()
        self.tree.edit_mco(
            mock_ui_info,
            self.tree.workflow_mv.mco_mv[0])

        self.assertEqual(
            self.tree.model.mco.edit_traits_call_count,
            1
        )

    def test_delete_mco(self):
        self.assertIsNotNone(self.tree.model.mco)

        mock_ui_info = mock.Mock()
        mock_object = mock.Mock()
        self.tree.delete_mco(mock_ui_info, mock_object)

        self.assertIsNone(self.tree.model.mco)

    def test_delete_mco_parameter(self):
        self.assertEqual(len(self.tree.model.mco.parameters), 1)

        mock_ui_info = mock.Mock()
        self.tree.delete_parameter(
            mock_ui_info,
            self.tree.workflow_mv.mco_mv[0].mco_parameters_mv[0])

        self.assertEqual(len(self.tree.model.mco.parameters), 0)

    def test_delete_execution_layer(self):
        first_execution_layer = self.tree.workflow_mv.execution_layers_mv[0]

        self.assertEqual(len(self.tree.workflow_mv.execution_layers_mv), 2)

        mock_ui_info = mock.Mock()
        self.tree.delete_layer(
            mock_ui_info,
            first_execution_layer)

        self.assertEqual(len(self.tree.workflow_mv.execution_layers_mv), 1)


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
