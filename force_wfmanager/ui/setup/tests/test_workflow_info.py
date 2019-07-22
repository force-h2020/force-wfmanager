from force_bdss.api import (
    KPISpecification, OutputSlotInfo
)

from force_bdss.tests.probe_classes.probe_extension_plugin import \
    ProbeExtensionPlugin
from force_wfmanager.ui.setup.workflow_info import WorkflowInfo
from force_wfmanager.ui.setup.workflow_view import \
    WorkflowView
from force_wfmanager.ui.setup.tests.template_test_case import (
    BaseTest
)


class TestWorkflowInfo(BaseTest):

    def setUp(self):
        super(TestWorkflowInfo, self).setUp()

        self.workflow.execution_layers[0].data_sources[0].output_slot_info \
            = [OutputSlotInfo(name='outputA'), OutputSlotInfo(name='outputX')]
        self.workflow.execution_layers[0].data_sources[1].output_slot_info \
            = [OutputSlotInfo(name='outputB')]

        self.mco_model.kpis.append(KPISpecification(name='outputA'))

        self.workflow_view = WorkflowView(
            model=self.workflow
        )

        # WorkflowInfo for testing
        self.other_plugin = ProbeExtensionPlugin()
        self.other_plugin.name = 'A different Probe extension'
        plugin_list = [self.plugin, self.other_plugin]

        self.workflow_info = WorkflowInfo(
            plugins=plugin_list,
            workflow_filename='workflow.json',
            selected_factory='Workflow',
            error_message=self.workflow_view.error_message
        )

    def test_init(self):
        self.assertEqual(len(self.workflow_info.plugin_names), 2)

    def test_plugin_list(self):
        self.assertEqual(self.workflow_info.plugin_names,
                         ['Probe extension', 'A different Probe extension'])

    def test_workflow_filename(self):
        self.assertEqual(self.workflow_info.workflow_filename_message,
                         'Current File: workflow.json')

    def test_error_messaging(self):
        self.assertIsNotNone(self.workflow_view.error_message)
