from envisage.api import Plugin
from envisage.ui.tasks.api import TaskFactory

from traits.api import List

from force_bdss.factory_registry_plugin import FACTORY_REGISTRY_PLUGIN_ID

from force_wfmanager.wfmanager_task import WfManagerTask

import os.path

from force_bdss.io.workflow_reader import WorkflowReader


class WfManagerPlugin(Plugin):
    """ The basic WfManager """

    TASKS = 'envisage.ui.tasks.tasks'

    id = 'force_wfmanager.wfmanager_plugin'
    name = 'Workflow Manager'
    workflow_file = '/Users/jjohnson/Force-Project-Test-Build/workflow_basic.json'

    tasks = List(contributes_to=TASKS)

    def _tasks_default(self):
        return [TaskFactory(id='force_wfmanager.wfmanager_task',
                            name='Workflow Manager',
                            factory=self._create_task)]

    def _create_task(self):
        factory_registry = self.application.get_plugin(
            FACTORY_REGISTRY_PLUGIN_ID)

        wf_manager_task = WfManagerTask(factory_registry=factory_registry)

        if self.workflow_file != '':
            if os.path.isfile(self.workflow_file) is False:
                # Warning here
                pass
            else:
                reader = WorkflowReader(factory_registry=factory_registry)

                wf_manager_task.workflow_m = reader.read(open(self.workflow_file,'r'))

        return wf_manager_task
