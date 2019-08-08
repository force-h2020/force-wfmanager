from force_wfmanager.ui.setup.side_pane import SidePane
from force_wfmanager.ui.setup.system_state import SystemState
from force_wfmanager.ui.setup.tests.wfmanager_base_test_case import (
    WfManagerBaseTestCase
)


class TestSidePane(WfManagerBaseTestCase):

    def setUp(self):
        super(TestSidePane, self).setUp()

        self.system_state = SystemState()

        self.side_pane = SidePane(
            workflow_model=self.workflow,
            factory_registry=self.factory_registry,
            system_state=self.system_state

        )

    def test_init_side_pane(self):
        self.assertEqual(
            self.workflow,
            self.side_pane.workflow_model
        )
        self.assertEqual(
            self.workflow,
            self.side_pane.workflow_tree.workflow_view.model
        )

        self.assertEqual(
            (self.side_pane.workflow_tree.workflow_view
             .process_view[0].execution_layer_views[0].model),
            self.workflow.execution_layers[0]
        )

        mco_view = self.side_pane.workflow_tree.workflow_view.mco_view[0]
        self.assertIsNotNone(mco_view)
        self.assertEqual(
            0,
            len(mco_view.kpi_view.model_views)
        )
        self.assertEqual(
            2,
            len(mco_view.parameter_view.model_views)
        )
