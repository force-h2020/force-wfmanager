from concurrent.futures import ThreadPoolExecutor
import os
import logging
import subprocess
import tempfile
import textwrap
from subprocess import SubprocessError

from pyface.api import (
    FileDialog,
    GUI,
    ImageResource,
    OK,
    YES,
    confirm,
    error,
    information,
)
from pyface.tasks.action.api import SMenu, SMenuBar, SToolBar, TaskAction
from pyface.tasks.api import PaneItem, Task, TaskLayout
from traits.api import Bool, File, Instance, List, on_trait_change, Str

from force_bdss.api import (
    BaseExtensionPlugin,
    BaseUIHooksManager,
    IFactoryRegistry,
    MCOStartEvent,
    MCOProgressEvent,
    MCORuntimeEvent,
    InvalidFileException,
    Workflow,
)

from force_wfmanager.io.workflow_io import (
    write_workflow_file,
    load_workflow_file,
)
from force_wfmanager.model.analysis_model import AnalysisModel
from force_wfmanager.plugins.plugin_dialog import PluginDialog
from force_wfmanager.server.zmq_server import ZMQServer
from force_wfmanager.ui import (
    ContributedUI,
    ContributedUIHandler,
    UISelectModal,
)
from force_wfmanager.ui.setup.setup_pane import SetupPane
from force_wfmanager.ui.setup.side_pane import SidePane
from force_wfmanager.ui.setup.system_state import SystemState

from force_wfmanager.wfmanager import TaskToggleGroupAccelerator
from force_wfmanager.io.project_io import load_analysis_model

from envisage.ui.tasks.task_extension import TaskExtension
from pyface.tasks.action.api import SchemaAddition
from traits.api import Callable


log = logging.getLogger(__name__)


class WfManagerGlobalTask(TaskExtension):
    """Global task: run/pause/stop workflow"""

    # The ID of the task to extend. If the ID is omitted, the extension applies
    # to all tasks.
    task_id = 'force_wfmanager.wfmanager_global_task'

    # A list of menu bar and tool bar items to add to the set provided
    # by the task.
    actions = List(SchemaAddition)

    # A list of dock pane factories that will extend the dock panes provided by
    # the task.
    dock_pane_factories = List(Callable)

    # ------------------
    #      Defaults
    # ------------------

    def _actions_default(self):

        return [
            SchemaAddition(
                path='MenuBar/View',
                factory=self.menu_bar,
                id='SomethingElse',
            ),
        ]

    def menu_bar(self):
        """A menu bar with functions relevant to the Setup task.
        """
        menu_bar = SMenuBar(
            SMenu(
                TaskAction(name="Exit", method="exit", accelerator="Ctrl+Q"),
                name="&Workflow Manager",
            ),
            SMenu(
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
                TaskAction(
                    name="Save Workflow as...",
                    method="save_workflow_as",
                    enabled_name="save_load_enabled",
                    accelerator="Shift+Ctrl+S",
                ),
                TaskAction(name="Plugins...", method="open_plugins"),
                TaskAction(name="Exit", method="exit"),
                # NOTE: Setting id='File' here will automatically create
                #       a exit menu item, I guess this is QT being 'helpful'.
                #       This menu item calls application.exit, which bypasses
                #       our custom exit which prompts for a save before exiting
                name="&File",
            ),
            SMenu(
                TaskAction(
                    name="About WorkflowManager...", method="open_about"
                ),
                name="&Help",
            ),
            SMenu(TaskToggleGroupAccelerator(), id="View", name="&View"),
        )
        return menu_bar

    def tool_bars_default(self):
        return [
            SToolBar(
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
                TaskAction(
                    name="Plugins",
                    tooltip="View state of loaded plugins",
                    image=ImageResource("baseline_power_black_48dp"),
                    method="open_plugins",
                    image_size=(64, 64),
                ),
            ),
        ]