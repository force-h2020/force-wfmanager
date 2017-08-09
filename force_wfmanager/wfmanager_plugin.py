from envisage.api import Plugin
from envisage.ui.tasks.api import TaskFactory

from traits.api import List

from force_bdss.factory_registry_plugin import FACTORY_REGISTRY_PLUGIN_ID

from force_wfmanager.wfmanager_task import WfManagerTask


class WfManagerPlugin(Plugin):
    """ The basic WfManager """

    TASKS = 'envisage.ui.tasks.tasks'

    id = 'force_wfmanager.wfmanager_plugin'
    name = 'Workflow Manager'

    tasks = List(contributes_to=TASKS)

    def _tasks_default(self):
        return [TaskFactory(id='force_wfmanager.wfmanager_task',
                            name='Workflow Manager',
                            factory=self._create_task)]

    def _create_task(self):
        factory_registry = self.application.get_plugin(
            FACTORY_REGISTRY_PLUGIN_ID)

        return WfManagerTask(factory_registry=factory_registry)
