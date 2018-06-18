from envisage.api import Plugin
from envisage.ui.tasks.api import TaskFactory

from traits.api import List

from pyface.api import confirm, YES

from force_bdss.factory_registry_plugin import FACTORY_REGISTRY_PLUGIN_ID

from force_wfmanager.wfmanager_task import WfManagerTask

import os.path

from force_bdss.io.workflow_reader import WorkflowReader


class WfManagerPlugin(Plugin):
    """ The basic WfManager """

    TASKS = 'envisage.ui.tasks.tasks'

    id = 'force_wfmanager.wfmanager_plugin'
    name = 'Workflow Manager'
    workflow_file = None

    tasks = List(contributes_to=TASKS)

    def _tasks_default(self):
        return [TaskFactory(id='force_wfmanager.wfmanager_task',
                            name='Workflow Manager',
                            factory=self._create_task)]

    def _create_task(self):
        factory_registry = self.application.get_plugin(
            FACTORY_REGISTRY_PLUGIN_ID)

        wf_manager_task = WfManagerTask(factory_registry=factory_registry)

        if self.workflow_file is not None:
            if os.path.isfile(self.workflow_file) is False:
                result = confirm(None, 'File at path \'{}\' not found.\n'
                                       'Load with empty workflow?'
                                 .format(os.path.abspath(self.workflow_file)))
                if result is not YES:
                    quit()

            else:
                reader = WorkflowReader(factory_registry=factory_registry)

                wf_manager_task.workflow_m = reader.read(open(
                    self.workflow_file, 'r'))

        return wf_manager_task
