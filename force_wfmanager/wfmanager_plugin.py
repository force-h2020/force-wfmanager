from envisage.api import Plugin
from envisage.ui.tasks.api import TaskFactory

from traits.api import List

from force_bdss.bundle_registry_plugin import BUNDLE_REGISTRY_PLUGIN_ID


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
        from force_wfmanager.wfmanager_task import WfManagerTask

        bundle_registry = self.application.get_plugin(
            BUNDLE_REGISTRY_PLUGIN_ID)

        return WfManagerTask(bundle_registry=bundle_registry)
