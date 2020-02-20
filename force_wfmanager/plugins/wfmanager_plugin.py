from envisage.api import Plugin
from envisage.ui.tasks.api import TaskFactory
from traits.api import Either, List, Str

from force_bdss.api import IFactoryRegistry
from force_wfmanager.ui import IContributedUI
from force_wfmanager.wfmanager_review_task import WfManagerReviewTask
from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask


class WfManagerPlugin(Plugin):
    """ The Plugin containing the Workflow Manager UI. This contains the
    factories which create the Tasks (currently Setup & Review)"""

    TASKS = 'envisage.ui.tasks.tasks'

    id = 'force_wfmanager.wfmanager_plugin'
    name = 'Workflow Manager'

    tasks = List(contributes_to=TASKS)

    workflow_file = Either(None, Str())

    # -----------------
    #      Defaults
    # -----------------

    def _tasks_default(self):
        return [TaskFactory(id='force_wfmanager.wfmanager_setup_task',
                            name='Workflow Manager (Setup)',
                            factory=self._create_setup_task),
                TaskFactory(id='force_wfmanager.wfmanager_review_task',
                            name='Workflow Manager (Review)',
                            factory=self._create_review_task)
                ]

    # -----------------
    #  Private Methods
    # -----------------

    def _create_setup_task(self):
        factory_registry = self.application.get_service(
            IFactoryRegistry
        )
        # Plugin contributed UIs targeted at a specific, predefined workflow
        contributed_uis = self.application.get_services(
            IContributedUI
        )
        wf_manager_setup_task = WfManagerSetupTask(
            factory_registry=factory_registry,
            contributed_uis=contributed_uis
        )
        if self.workflow_file is not None:
            wf_manager_setup_task.load_workflow(self.workflow_file)

        return wf_manager_setup_task

    def _create_review_task(self):
        factory_registry = self.application.get_service(
            IFactoryRegistry
        )
        wf_manager_review_task = WfManagerReviewTask(
            factory_registry=factory_registry
        )

        return wf_manager_review_task
