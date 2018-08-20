import logging
import textwrap

from envisage.ui.tasks.tasks_application import TasksApplication
from force_bdss.io.workflow_reader import InvalidFileException, WorkflowReader
from force_bdss.io.workflow_writer import WorkflowWriter
from force_bdss.ui_hooks.base_ui_hooks_manager import BaseUIHooksManager

from pyface.api import ImageResource
from pyface.constant import OK
from pyface.file_dialog import FileDialog
from pyface.message_dialog import error, information
from pyface.tasks.action.api import SMenuBar, SMenu, TaskAction, SToolBar
from pyface.tasks.action.schema_addition import SchemaAddition
from pyface.tasks.api import Task, TaskLayout, PaneItem

from traits.api import Instance, on_trait_change, List, Bool

from force_bdss.api import IFactoryRegistryPlugin, Workflow

from force_wfmanager.central_pane.analysis_model import AnalysisModel
from force_wfmanager.central_pane.setup_pane import SetupPane
from force_wfmanager.left_side_pane.tree_pane import TreePane
from force_wfmanager.TaskToggleGroupAccelerator import (
    TaskToggleGroupAccelerator
)
from traits.trait_types import File

log = logging.getLogger(__name__)


class WfManagerSetupTask(Task):
    id = 'force_wfmanager.wfmanager_setup_task'
    name = 'Workflow Setup'

    #: Workflow model.
    workflow_m = Instance(Workflow, allow_none=False)

    #: Registry of the available factories
    factory_registry = Instance(IFactoryRegistryPlugin)

    #: Current workflow file on which the application is writing
    current_file = File()

    #: Side Pane containing the tree editor for the Workflow and the Run button
    side_pane = Instance(TreePane)

    #: The menu bar for this task.
    menu_bar = Instance(SMenuBar)

    #: The tool bars for this task.
    tool_bars = List(SToolBar)

    #: Is the 'run' toolbar button active
    run_enabled = Bool(True)

    #: Are the saving and loading menu/toolbar buttons active
    save_load_enabled = Bool(True)

    #: A list of UI hooks managers. These hold plugin injected "hook managers",
    #: classes with methods that are called when some operation is performed
    #: by the UI
    ui_hooks_managers = List(BaseUIHooksManager)

    task_group = Instance(TaskToggleGroupAccelerator)

    def __init__(self, factory_registry, *args, **kwargs):
        self.factory_registry = factory_registry
        super(WfManagerSetupTask, self).__init__(*args, **kwargs)

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
                name='&Workflow Manager',

            ),
            SMenu(
                TaskAction(
                    name='Open Workflow...',
                    method='open_workflow',
                    enabled_name='save_load_enabled',
                    accelerator='Ctrl+O',
                ),
                TaskAction(
                    id='Save',
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
                name='&File',
                id='File'
            ),
            SMenu(
                TaskAction(
                    name='About WorkflowManager...',
                    method='open_about'
                ),
                name='&Help'
            ),
            SMenu(TaskToggleGroupAccelerator(), id='View', name='&View'),
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
        return SetupPane()

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

    def _workflow_m_default(self):
        return Workflow()

    def _ui_hooks_managers_default(self):
        hooks_factories = self.factory_registry.ui_hooks_factories
        managers = []
        for factory in hooks_factories:
            try:
                managers.append(
                    factory.create_ui_hooks_manager()
                )
            except Exception:
                log.exception(
                    "Failed to create UI "
                    "hook manager by factory {}".format(
                        factory.__class__.__name__)
                )
        return managers

    # Workflow Methods

    def open_workflow_file(self, f_name):
        """ Opens a workflow from the specified file name"""
        reader = WorkflowReader(self.factory_registry)
        try:
            with open(f_name, 'r') as fobj:
                self.workflow_m = reader.read(fobj)
        except InvalidFileException as e:
            error(
                None,
                'Cannot read the requested file:\n\n{}'.format(
                    str(e)),
                'Error when reading file'
            )
        else:
            self.current_file = f_name

    def save_workflow(self):
        """ Saves the workflow into the currently used file. If there is no
        current file, it shows a dialog """
        if len(self.current_file) == 0:
            return self.save_workflow_as()

        if not self._write_workflow(self.current_file):
            self.current_file = ''
            return False
        return True

    def save_workflow_as(self):
        """ Shows a dialog to save the workflow into a JSON file """
        dialog = FileDialog(
            action="save as",
            default_filename="workflow.json",
            wildcard='JSON files (*.json)|*.json|'
        )

        result = dialog.open()

        if result is not OK:
            return

        current_file = dialog.path

        if self._write_workflow(current_file):
            self.current_file = current_file
            return True
        return False

    def _write_workflow(self, file_path):
        """ Creates a JSON file in the file_path and write the workflow
        description in it

        Parameters
        ----------
        file_path: str
            The file_path pointing to the file in which you want to write the
            workflow

        Returns
        -------
        Boolean:
            True if it was a success to write in the file, False otherwise
        """
        for hook_manager in self.ui_hooks_managers:
            try:
                hook_manager.before_save(self)
            except Exception:
                log.exception(
                    "Failed before_save hook "
                    "for hook manager {}".format(
                        hook_manager.__class__.__name__)
                )

        try:
            with open(file_path, 'w') as output:
                WorkflowWriter().write(self.workflow_m, output)
        except IOError as e:
            error(
                None,
                'Cannot save in the requested file:\n\n{}'.format(
                    str(e)),
                'Error when saving workflow'
            )
            log.exception('Error when saving workflow')
            return False
        except Exception as e:
            error(
                None,
                'Cannot save the workflow:\n\n{}'.format(
                    str(e)),
                'Error when saving workflow'
            )
            log.exception('Error when saving workflow')
            return False
        else:
            return True

    def open_workflow(self):
        """ Shows a dialog to open a workflow file """
        dialog = FileDialog(
            action="open",
            wildcard='JSON files (*.json)|*.json|'
        )
        result = dialog.open()
        f_name = dialog.path
        if result is OK:
            self.open_workflow_file(f_name)

    def open_about(self):
        information(
            None,
            textwrap.dedent(
                """
                Workflow Manager: a UI application for Business Decision System.

                Developed as part of the FORCE project (Horizon 2020/NMBP-23-2016/721027).

                This software is released under the BSD license.
                """,  # noqa
            ),
            "About WorkflowManager"
        )

    # Sync Handlers

    # Inbound handlers

    @on_trait_change('side_pane.run_enabled')
    def set_toolbar_run_btn_state(self):
        self.run_enabled = self.side_pane.run_enabled

    @on_trait_change('window.application.computation_running')
    def update_side_pane_status(self):
        if self.window is not None:
            self.side_pane.ui_enabled = not self.window.application.computation_running
            self.save_load_enabled = not self.window.application.computation_running

    # Outbound Handlers

    @on_trait_change('run_enabled')
    def update_wfmanager_run_enabled(self):
        if self.window is not None:
            self.window.application.run_enabled = self.run_enabled

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
        self.window.application.exit()

    def open_plugins(self):
        self.window.application.open_plugins()

    def run_bdss(self):
        task = self.window.get_task('force_wfmanager.wfmanager_results_task')
        task.initialized()
        task.run_bdss()
