from envisage.api import Plugin
from envisage.ui.tasks.api import TaskFactory
from traits.api import Either, List, Unicode

from force_bdss.api import IFactoryRegistry
from force_wfmanager.io.workflow_io import write_workflow_file
from force_wfmanager.wfmanager_results_task import WfManagerResultsTask
from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask


class WfManagerPlugin(Plugin):
    """ The Plugin containing the Workflow Manager UI. This contains the
    factories which create the Tasks (currently Setup & Results)"""

    TASKS = 'envisage.ui.tasks.tasks'

    id = 'force_wfmanager.wfmanager_plugin'
    name = 'Workflow Manager'

    tasks = List(contributes_to=TASKS)

    workflow_file = Either(None, Unicode())

    def _tasks_default(self):
        return [TaskFactory(id='force_wfmanager.wfmanager_setup_task',
                            name='Workflow Manager (Setup)',
                            factory=self._create_setup_task),
                TaskFactory(id='force_wfmanager.wfmanager_results_task',
                            name='Workflow Manager (Results)',
                            factory=self._create_results_task)
                ]

    def _create_setup_task(self):
        factory_registry = self.application.get_service(
            IFactoryRegistry
        )
        wf_manager_setup_task = WfManagerSetupTask(
            factory_registry=factory_registry,
        )
        if self.workflow_file is not None:
            wf_manager_setup_task._load_workflow(self.workflow_file)

        return wf_manager_setup_task

    def _create_results_task(self):
        factory_registry = self.application.get_service(
            IFactoryRegistry
        )
        wf_manager_results_task = WfManagerResultsTask(
            factory_registry=factory_registry
        )

        return wf_manager_results_task