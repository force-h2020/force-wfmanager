from envisage.api import Plugin
from envisage.ui.tasks.api import TaskFactory

from traits.api import List

from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask
from force_wfmanager.wfmanager_results_task import WfManagerResultsTask


class WfManagerPlugin(Plugin):
    """ The basic WfManager """

    TASKS = 'envisage.ui.tasks.tasks'

    id = 'force_wfmanager.wfmanager_plugin'
    name = 'Workflow Manager'

    tasks = List(contributes_to=TASKS)

    def _tasks_default(self):
        return [TaskFactory(id='force_wfmanager.wfmanager_setup_task',
                            name='Workflow Manager (Setup)',
                            factory=self._create_setup_task),
                TaskFactory(id='force_wfmanager.wfmanager_results_task',
                            name='Workflow Manager (Results)',
                            factory=self._create_results_task)
                ]

    def _create_setup_task(self):
        wf_manager_setup_task = WfManagerSetupTask()
        return wf_manager_setup_task

    def _create_results_task(self):
        wf_manager_results_task = WfManagerResultsTask()
        return wf_manager_results_task
