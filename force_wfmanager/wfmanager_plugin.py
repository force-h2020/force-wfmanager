from envisage.api import Plugin
from envisage.ui.tasks.api import TaskFactory

from traits.api import List, Instance

from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask
from force_wfmanager.wfmanager_results_task import WfManagerResultsTask

from pyface.tasks.action.api import (
    SMenu, SMenuBar, TaskAction,
)
from force_wfmanager.TaskToggleGroupAccelerator import (
    TaskToggleGroupAccelerator
)


class WfManagerPlugin(Plugin):
    """ The basic WfManager """

    TASKS = 'envisage.ui.tasks.tasks'

    id = 'force_wfmanager.wfmanager_plugin'
    name = 'Workflow Manager'
    shared_menu_bar = Instance(SMenuBar)

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

        wf_manager_setup_task = WfManagerSetupTask(
            shared_menu_bar=self.shared_menu_bar
        )

        return wf_manager_setup_task

    def _create_results_task(self):

        wf_manager_results_task = WfManagerResultsTask(
            shared_menu_bar=self.shared_menu_bar
        )

        return wf_manager_results_task

    def _shared_menu_bar_default(self):
        """A menu bar with elements shared between the different tasks.
        Elements unique to a specific task are added when the task is
        instantiated. Functions associated to the shared methods are located
        at the application level."""
        menu_bar_shared = SMenuBar(
            SMenu(
                TaskAction(
                    name='Exit',
                    method='app.exit',
                    accelerator='Ctrl+Q',
                ),
                name='&Workflow Manager'
            ),
            SMenu(
                TaskAction(
                    name='Open Workflow...',
                    method='app.open_workflow',
                    enabled_name='app.save_load_enabled',
                    accelerator='Ctrl+O',
                ),
                TaskAction(
                    name='Save Workflow',
                    method='app.save_workflow',
                    enabled_name='app.save_load_enabled',
                    accelerator='Ctrl+S',
                ),
                TaskAction(
                    name='Save Workflow as...',
                    method='app.save_workflow_as',
                    enabled_name='app.save_load_enabled',
                    accelerator='Shift+Ctrl+S',
                ),
                TaskAction(
                    name='Plugins...',
                    method='app.open_plugins'
                ),
                name='&File'
            ),
            SMenu(
                TaskAction(
                    name='About WorkflowManager...',
                    method='app.open_about'
                ),
                name='&Help'
            ),
            SMenu(TaskToggleGroupAccelerator(), id='View', name='&View')
        )
        return menu_bar_shared
