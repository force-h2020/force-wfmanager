from envisage.api import Plugin
from envisage.ui.tasks.api import TaskFactory
from envisage.ui.tasks.task_extension import TaskExtension
from force_wfmanager.central_pane.analysis_model import AnalysisModel
from force_bdss.api import Workflow
from pyface.action.action import Action
from pyface.action.action_item import ActionItem
from pyface.tasks.action.schema_addition import SchemaAddition
from pyface.tasks.action.task_action import TaskAction
from traits.api import List

from force_wfmanager.wfmanager_results_task import WfManagerResultsTask
from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask
from force_bdss.api import FACTORY_REGISTRY_PLUGIN_ID


class WfManagerPlugin(Plugin):
    """ The basic WfManager """

    TASKS = 'envisage.ui.tasks.tasks'

    TASK_EXTENSIONS = 'envisage.ui.tasks.task_extensions'

    id = 'force_wfmanager.wfmanager_plugin'
    name = 'Workflow Manager'

    tasks = List(contributes_to=TASKS)
    task_extensions = List(contributes_to=TASK_EXTENSIONS)

    def __init__(self, workflow_file):
        super(WfManagerPlugin, self).__init__()
        # Things to be shared between both the tasks
        self.workflow_file = workflow_file

    def _tasks_default(self):
        return [TaskFactory(id='force_wfmanager.wfmanager_setup_task',
                            name='Workflow Manager (Setup)',
                            factory=self._create_setup_task),
                TaskFactory(id='force_wfmanager.wfmanager_results_task',
                            name='Workflow Manager (Results)',
                            factory=self._create_results_task)
                ]

    def _task_extensions_default(self):
        return [TaskExtension(
            actions=[SchemaAddition(
                factory=self._exit_action,
                path='MenuBar/File')]
            )
        ]

    def _create_setup_task(self):
        factory_registry = self.application.get_plugin(
            FACTORY_REGISTRY_PLUGIN_ID)
        print (self.application)
        wf_manager_setup_task = WfManagerSetupTask(
            factory_registry=factory_registry,
        )
        if self.workflow_file is not None:
            wf_manager_setup_task.open_workflow_file(self.workflow_file)

        return wf_manager_setup_task

    def _create_results_task(self):
        factory_registry = self.application.get_plugin(
            FACTORY_REGISTRY_PLUGIN_ID)
        wf_manager_results_task = WfManagerResultsTask(
            factory_registry=factory_registry
        )

        return wf_manager_results_task

    def _exit_action(self):
        return ActionItem(
            action=Action(
                name='Exit',
                on_perform=self.application.exit
            )
        )
