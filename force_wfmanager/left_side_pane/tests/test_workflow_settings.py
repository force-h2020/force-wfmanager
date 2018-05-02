import unittest

from force_bdss.core.execution_layer import ExecutionLayer
from force_bdss.data_sources.base_data_source_model import BaseDataSourceModel
from force_bdss.mco.base_mco_model import BaseMCOModel

try:
    import mock
except ImportError:
    from unittest import mock

from traits.api import Instance, HasTraits, Int

from force_bdss.tests.probe_classes.mco import (
    ProbeParameterFactory, ProbeMCOFactory, ProbeMCOModel)
from force_bdss.tests.probe_classes.data_source import ProbeDataSourceFactory
from force_bdss.core.workflow import Workflow

from force_wfmanager.left_side_pane.workflow_model_view import \
    WorkflowModelView
from force_wfmanager.left_side_pane.workflow_settings import (
    WorkflowSettings, TreeNodeWithStatus)
from force_wfmanager.left_side_pane.new_entity_modal import NewEntityModal


NEW_ENTITY_MODAL_PATH = \
    "force_wfmanager.left_side_pane.workflow_settings.NewEntityModal"


def mock_new_modal(model_type):
    def _mock_new_modal(*args, **kwargs):
        modal = mock.Mock(spec=NewEntityModal)
        modal.edit_traits = lambda: None

        # Any type is ok as long as it passes trait validation.
        # We choose BaseDataSourceModel.
        modal.current_model = model_type(factory=None)
        return modal

    return _mock_new_modal


class WorkflowSettingsEditor(HasTraits):
    object = Instance(WorkflowSettings)


def get_workflow_settings():
    return WorkflowSettings(
        mco_factories=[ProbeMCOFactory(None)],
        data_source_factories=[ProbeDataSourceFactory(None)],
        model=Workflow(),
    )


class ProbeMCOModelEditable(ProbeMCOModel):
    edit_traits_call_count = Int(0)

    def edit_traits(self, *args, **kwargs):
        self.edit_traits_call_count += 1


def get_workflow_model_view():
    mco_factory = ProbeMCOFactory(None, model_class=ProbeMCOModelEditable)
    mco = mco_factory.create_model()

    parameter = ProbeParameterFactory(None).create_model()
    parameter.name = ''
    mco.parameters = [parameter]

    data_source_factory = ProbeDataSourceFactory(None)

    workflow_mv = WorkflowModelView(
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
    return workflow_mv


def get_workflow_settings_editor(workflow_model_view):
    return WorkflowSettingsEditor(
        object=WorkflowSettings(
            workflow_mv=workflow_model_view,
            model=workflow_model_view.model
        )
    )


class TestWorkflowSettings(unittest.TestCase):
    def setUp(self):
        self.workflow_settings = get_workflow_settings()

        self.settings = self.workflow_settings

    def test_ui_initialization(self):
        self.assertIsNone(self.settings.model.mco)
        self.assertEqual(len(self.settings.model.execution_layers), 0)
        self.assertEqual(len(self.settings.workflow_mv.mco_mv), 0)
        self.assertEqual(len(self.settings.workflow_mv.execution_layers_mv), 0)


class TestTreeEditorHandler(unittest.TestCase):
    def setUp(self):
        self.workflow_mv = get_workflow_model_view()

        self.workflow_settings_editor = get_workflow_settings_editor(
            self.workflow_mv)
        self.workflow_settings = self.workflow_settings_editor.object

    def test_new_mco(self):
        with mock.patch(NEW_ENTITY_MODAL_PATH) as mock_modal:
            mock_modal.side_effect = mock_new_modal(BaseMCOModel)
            mock_ui_info = mock.Mock()
            mock_object = mock.Mock()

            self.workflow_settings.new_mco(mock_ui_info, mock_object)

            mock_modal.assert_called()

    def test_new_mco_parameter(self):
        with mock.patch(NEW_ENTITY_MODAL_PATH) as mock_modal:
            mock_modal.side_effect = mock_new_modal(BaseMCOModel)
            mock_ui_info = mock.Mock()
            mock_object = mock.Mock()

            self.workflow_settings.new_parameter(mock_ui_info, mock_object)

            mock_modal.assert_called()
            mock_object.add_parameter.assert_called()

    def test_new_data_source(self):
        with mock.patch(NEW_ENTITY_MODAL_PATH) as mock_modal:
            mock_modal.side_effect = mock_new_modal(BaseDataSourceModel)
            mock_ui_info = mock.Mock()
            mock_object = mock.Mock()

            self.workflow_settings.new_data_source(mock_ui_info, mock_object)

            mock_modal.assert_called()
            mock_object.add_data_source.assert_called()

    def test_edit_entity(self):
        self.workflow_settings.edit_mco(
            self.workflow_settings_editor,
            self.workflow_mv.mco_mv[0])

        self.assertEqual(
            self.workflow_mv.model.mco.edit_traits_call_count,
            1
        )

    def test_delete_mco(self):
        self.assertIsNotNone(self.workflow_mv.model.mco)

        mock_ui_info = mock.Mock()
        mock_object = mock.Mock()
        self.workflow_settings.delete_mco(mock_ui_info, mock_object)

        self.assertIsNone(self.workflow_mv.model.mco)

    def test_delete_mco_parameter(self):
        self.assertEqual(len(self.workflow_mv.model.mco.parameters), 1)

        mock_ui_info = mock.Mock()
        self.workflow_settings.delete_parameter(
            mock_ui_info,
            self.workflow_mv.mco_mv[0].mco_parameters_mv[0])

        self.assertEqual(len(self.workflow_mv.model.mco.parameters), 0)

    def test_delete_execution_layer(self):
        first_execution_layer = self.workflow_mv.execution_layers_mv[0]

        self.assertEqual(len(self.workflow_mv.execution_layers_mv), 2)

        mock_ui_info = mock.Mock()
        self.workflow_settings.delete_layer(
            mock_ui_info,
            first_execution_layer)

        self.assertEqual(len(self.workflow_mv.execution_layers_mv), 1)


class TestWorkflowElementNode(unittest.TestCase):
    def test_wfelement_node(self):
        wfelement_node = TreeNodeWithStatus()
        wf_mv = get_workflow_model_view()
        self.assertEqual(wfelement_node.get_icon(wf_mv, False),
                         'icons/valid.png')
        wf_mv.valid = False
        self.assertEqual(wfelement_node.get_icon(wf_mv, False),
                         'icons/invalid.png')

        self.assertEqual(
            wfelement_node.get_icon(
                wf_mv.mco_mv[0].mco_parameters_mv[0],
                False),
            'icons/valid.png')
