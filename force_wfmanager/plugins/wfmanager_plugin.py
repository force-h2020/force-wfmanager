from envisage.api import Plugin
from envisage.ui.tasks.api import TaskFactory
from traits.api import Either, List, Str


from force_bdss.api import IFactoryRegistry
from force_wfmanager.ui import IContributedUI
from force_wfmanager.wfmanager_review_task import WfManagerReviewTask
from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask
from force_wfmanager.wfmanager_global_task import WfManagerGlobalTask

from pyface.tasks.action.api import SchemaAddition
from pyface.tasks.action.api import SMenu, SMenuBar, SToolBar, TaskAction, SGroup
from pyface.api import ImageResource, FileDialog, OK, error

class WfManagerPlugin(Plugin):
    """ The Plugin containing the Workflow Manager UI. This contains the
    factories which create the Tasks (currently Setup & Review)"""

    id = 'force_wfmanager.wfmanager_plugin'
    name = 'Workflow Manager'

    tasks = List(contributes_to='envisage.ui.tasks.tasks')

    contributed_task_extensions = \
        List(contributes_to='envisage.ui.tasks.task_extensions')

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
                            factory=self._create_review_task),
                ]

    def _contributed_task_extensions_default(self):
        return [WfManagerGlobalTask()]

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

        wf_manager_setup_task.extra_actions = [
            SchemaAddition(
                path='mymenu/Help',
                factory=self.menuxbar,
                id='SomethingElse',
            ),
            SchemaAddition(
                path='',
                factory=self.toolxbar,
                id='SomethingElse',
            ),
        ]
        #wf_manager_setup_task.create_with_extensions(WfManagerGlobalTask())

        if self.workflow_file is not None:
            wf_manager_setup_task.load_workflow(self.workflow_file)

        return wf_manager_setup_task

    def menuxbar(self):
        """A menu bar with functions relevant to the Setup task.
        """
        menu = SMenu(
                TaskAction(
                    name="Open Workflow...",
                    method="open_workflow",
                    enabled_name="save_load_enabled",
                    accelerator="Ctrl+O",
                ),
                TaskAction(
                    id="Save",
                    name="Save Workflow",
                    method="save_workflow",
                    enabled_name="save_load_enabled",
                    accelerator="Ctrl+S",
                ),
            )
        menu.name = 'DO X'
        menu_bar = SGroup(menu, id='globe')
        return menu_bar

    def toolxbar(self):
        tool = SToolBar(
            TaskAction(
                name="Run",
                tooltip="Run Workflow",
                image=ImageResource("baseline_play_arrow_black_48dp"),
                method="run_bdss",
                enabled_name="run_enabled",
                image_size=(64, 64),
            ),
            TaskAction(
                name="Stop",
                tooltip="Stop Workflow",
                method="stop_bdss",
                enabled_name="computation_running",
                image=ImageResource("baseline_stop_black_18dp"),
                image_size=(64, 64),
            ),
            TaskAction(
                name=" Pause",
                tooltip="Pause Workflow",
                method="pause_bdss",
                enabled_name="computation_running",
                image=ImageResource("baseline_pause_black_18dp"),
                image_size=(64, 64),
            ),
        )

        tool.name = 'DO X'
        tool_bar = SGroup(tool, id='globe')
        return tool_bar

    def _create_review_task(self):
        factory_registry = self.application.get_service(
            IFactoryRegistry
        )
        wf_manager_review_task = WfManagerReviewTask(
            factory_registry=factory_registry
        )

        return wf_manager_review_task

