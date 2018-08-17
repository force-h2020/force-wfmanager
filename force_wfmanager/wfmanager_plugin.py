from envisage.api import Plugin
from envisage.ui.tasks.api import TaskFactory

from traits.api import List

from force_wfmanager.wfmanager_results_task import WfManagerResultsTask
from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask


class WfManagerPlugin(Plugin):
    """ The basic WfManager """

    TASKS = 'envisage.ui.tasks.tasks'

    id = 'force_wfmanager.wfmanager_plugin'
    name = 'Workflow Manager'

    tasks = List(contributes_to=TASKS)

    def __init__(self, analysis_m, workflow_m, factory_registry):
        super(WfManagerPlugin, self).__init__()
        self.analysis_m = analysis_m
        self.workflow_m = workflow_m
        self.factory_registry = factory_registry

    def _tasks_default(self):
        return [TaskFactory(id='force_wfmanager.wfmanager_setup_task',
                            name='Workflow Manager (Setup)',
                            factory=self._create_setup_task),
                TaskFactory(id='force_wfmanager.wfmanager_results_task',
                            name='Workflow Manager (Results)',
                            factory=self._create_results_task)
                ]

    def _create_setup_task(self):
        wf_manager_setup_task = WfManagerSetupTask(
            analysis_m=self.analysis_m, workflow_m=self.workflow_m,
            factory_registry=self.factory_registry
        )
        return wf_manager_setup_task

    def _create_results_task(self):
        wf_manager_results_task = WfManagerResultsTask(
            analysis_m=self.analysis_m, workflow_m=self.workflow_m,
            factory_registry=self.factory_registry
        )
        return wf_manager_results_task
