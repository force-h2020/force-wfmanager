import logging

from envisage.ui.tasks.tasks_application import TasksApplication

from pyface.api import ImageResource
from pyface.tasks.action.api import SMenuBar, SMenu, TaskAction, SToolBar
from pyface.tasks.api import Task, TaskLayout, PaneItem

from traits.api import Instance, on_trait_change, List, Bool

from force_bdss.api import IFactoryRegistryPlugin, Workflow

from force_wfmanager.central_pane.analysis_model import AnalysisModel
from force_wfmanager.central_pane.setup_pane import SetupPane
from force_wfmanager.left_side_pane.tree_pane import TreePane
from force_wfmanager.TaskToggleGroupAccelerator import (
    TaskToggleGroupAccelerator
)
log = logging.getLogger(__name__)


class WfManagerSetupTask(Task):
    id = 'force_wfmanager.wfmanager_setup_task'
    name = 'Workflow Setup'

    #: Workflow model.
    workflow_m = Instance(Workflow, allow_none=False)

    #: Analysis model. Contains the results that are displayed in the plot
    #: and table
    analysis_m = Instance(AnalysisModel, allow_none=False)

    #: Registry of the available factories
    factory_registry = Instance(IFactoryRegistryPlugin)

    #: Side Pane containing the tree editor for the Workflow and the Run button
    side_pane = Instance(TreePane)

    #: The application associated with this Task. Effectively just a rename of
    #: window.application
    app = Instance(TasksApplication)

    #: The menu bar for this task.
    menu_bar = Instance(SMenuBar)

    #: The tool bars for this task.
    tool_bars = List(SToolBar)

    #: Is the 'run' toolbar button active
    run_enabled = Bool(True)

    #: Are the saving and loading menu/toolbar buttons active
    save_load_enabled = Bool(True)

    task_group = Instance(TaskToggleGroupAccelerator)

    def __init__(self, analysis_m, workflow_m, factory_registry):
        super(WfManagerSetupTask, self).__init__()
        self.analysis_m = analysis_m
        self.workflow_m = workflow_m
        self.factory_registry = factory_registry

    def _menu_bar_default(self):
        """A menu bar with functions relevant to the Setup task.
        Functions associated to the shared methods are located
        at the application level."""
        menu_bar = SMenuBar(
            SMenu(
                TaskAction(
                    name='Exit',
                    method='exit',
                    accelerator='Ctrl+Q',
                ),
                name='&Workflow Manager'
            ),
            SMenu(
                TaskAction(
                    name='Open Workflow...',
                    method='open_workflow',
                    enabled_name='save_load_enabled',
                    accelerator='Ctrl+O',
                ),
                TaskAction(
                    name='Save Workflow',
                    method='save_workflow',
                    enabled_name='save_load_enabled',
                    accelerator='Ctrl+S',
                ),
                TaskAction(
                    name='Save Workflow as...',
                    method='save_workflow_as',
                    enabled_name='save_load_enabled',
                    accelerator='Shift+Ctrl+S',
                ),
                TaskAction(
                    name='Plugins...',
                    method='open_plugins'
                ),
                name='&File'
            ),
            SMenu(
                TaskAction(
                    name='About WorkflowManager...',
                    method='open_about'
                ),
                name='&Help'
            ),
            SMenu(TaskToggleGroupAccelerator(), id='View', name='&View')
        )
        return menu_bar

    def _tool_bars_default(self):
        return [
            SToolBar(
                TaskAction(
                    name="View Results",
                    tooltip="View Results",
                    image=ImageResource("baseline_bar_chart_black_48dp"),
                    method="switch_task",
                    image_size=(64, 64)
                )
            ),
            SToolBar(
                TaskAction(
                    name="Open",
                    tooltip="Open workflow",
                    image=ImageResource("baseline_folder_open_black_48dp"),
                    method="open_workflow",
                    enabled_name="save_load_enabled",
                    image_size=(64, 64)
                ),
                TaskAction(
                    name="Save",
                    tooltip="Save workflow",
                    image=ImageResource("baseline_save_black_48dp"),
                    method="save_workflow",
                    enabled_name="save_load_enabled",
                    image_size=(64, 64)
                ),
                TaskAction(
                    name="Save As",
                    tooltip="Save workflow with new filename",
                    image=ImageResource("outline_save_black_48dp"),
                    method="save_workflow_as",
                    enabled_name="save_load_enabled",
                    image_size=(64, 64)
                ),
                TaskAction(
                    name="Plugins",
                    tooltip="View state of loaded plugins",
                    image=ImageResource("baseline_power_black_48dp"),
                    method="open_plugins",
                    image_size=(64, 64)
                ),
            ),
            SToolBar(
                TaskAction(
                    name="Run",
                    tooltip="Run Workflow",
                    image=ImageResource("baseline_play_arrow_black_48dp"),
                    method="run_bdss",
                    enabled_name="run_enabled",
                    image_size=(64, 64)
                ),
            )
        ]

    def create_central_pane(self):
        """ Creates the central pane which contains the analysis part
        (pareto front and output KPI values)
        """
        return SetupPane(self.analysis_m)

    def create_dock_panes(self):
        """ Creates the dock panes """
        return [self.side_pane]

    # Default initializers

    def _default_layout_default(self):
        """ Defines the default layout of the task window """
        return TaskLayout(
            left=PaneItem('force_wfmanager.tree_pane'),
        )

    def _side_pane_default(self):
        return TreePane(
            factory_registry=self.factory_registry,
            workflow_m=self.workflow_m
        )

    def _app_default(self):
        return self.window.application

    # Sync Handlers

    # Inbound handlers
    @on_trait_change('app.workflow_m')
    def sync_workflow_m(self):
        self.workflow_m = self.app.workflow_m

    @on_trait_change('app.analysis_m')
    def sync_analysis_m(self):
        self.analysis_m = self.app.analysis_m

    @on_trait_change('app.factory_registry')
    def sync_factory_registry(self):
        self.factory_registry = self.app.factory_registry

    @on_trait_change('side_pane.run_enabled')
    def set_toolbar_run_btn_state(self):
        self.run_enabled = self.side_pane.run_enabled

    @on_trait_change('app.computation_running')
    def update_side_pane_status(self):
        self.side_pane.ui_enabled = not self.app.computation_running
        self.save_load_enabled = not self.app.computation_running

    # Outbound Handlers

    @on_trait_change('workflow_m')
    def update_side_pane(self):
        self.side_pane.workflow_m = self.workflow_m

    @on_trait_change('run_enabled')
    def update_wfmanager_run_enabled(self):
        self.app.run_enabled = self.run_enabled

    # Menu/Toolbar Methods

    def switch_task(self):
        """Switches to the results task and verifies startup setting are
        correct for toolbars/menus etc."""
        results_task = self.window.get_task(
            'force_wfmanager.wfmanager_results_task'
        )
        results_task.run_enabled = self.run_enabled
        self.window.activate_task(results_task)

    def exit(self):
        self.app.exit()

    def open_workflow(self):
        self.app.open_workflow()

    def save_workflow(self):
        self.app.save_workflow()

    def save_workflow_as(self):
        self.app.save_workflow_as()

    def open_plugins(self):
        self.app.open_plugins()

    def open_about(self):
        self.app.open_about()

    def run_bdss(self):
        self.app.run_bdss()
