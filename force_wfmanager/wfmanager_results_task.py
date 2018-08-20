import logging
import subprocess
import tempfile
import os
from concurrent.futures import ThreadPoolExecutor

from force_bdss.ui_hooks.base_ui_hooks_manager import BaseUIHooksManager
from force_wfmanager.server.zmq_server import ZMQServer

from pyface.api import ImageResource, confirm, YES, error, GUI
from pyface.tasks.action.api import SMenuBar, SMenu, TaskAction, SToolBar
from pyface.tasks.api import Task, TaskLayout, PaneItem

from traits.api import Bool, Instance, List, on_trait_change, Unicode

from force_bdss.api import (IFactoryRegistryPlugin, Workflow, WorkflowWriter,
                            MCOStartEvent, MCOProgressEvent,
                            BaseExtensionPlugin)

from force_wfmanager.central_pane.analysis_model import AnalysisModel
from force_wfmanager.central_pane.graph_pane import GraphPane
from force_wfmanager.left_side_pane.results_pane import ResultsPane
from force_wfmanager.plugin_dialog import PluginDialog
from force_wfmanager.TaskToggleGroupAccelerator import (
    TaskToggleGroupAccelerator
)

log = logging.getLogger(__name__)


class WfManagerResultsTask(Task):
    """Task responsible for running the Workflow and displaying the results."""

    id = 'force_wfmanager.wfmanager_results_task'
    name = 'Results'

    #: Workflow model.
    workflow_m = Instance(Workflow, allow_none=False)

    #: Analysis model. Contains the results that are displayed in the plot
    #: and table
    analysis_m = Instance(AnalysisModel, allow_none=False)

    #: Registry of the available factories
    factory_registry = Instance(IFactoryRegistryPlugin)

    #: Side Pane containing the tree editor for the Workflow and the Run button
    side_pane = Instance(ResultsPane)

    #: The menu bar for this task.
    menu_bar = Instance(SMenuBar)

    #: The tool bar for this task.
    tool_bars = List(SToolBar)

    #: Is the 'run' toolbar button active
    run_enabled = Bool(True)

    #: Are the saving and loading menu/toolbar buttons active
    save_load_enabled = Bool(True)

    #: A list of UI hooks managers. These hold plugin injected "hook managers",
    #: classes with methods that are called when some operation is performed
    #: by the UI
    ui_hooks_managers = List(BaseUIHooksManager)

    #: The thread pool executor to spawn the BDSS CLI process.
    executor = Instance(ThreadPoolExecutor)

    #: Path to spawn for the BDSS CLI executable.
    #: This will go to some global configuration option later.
    bdss_executable_path = Unicode("force_bdss")

    #: ZeroMQ Server to receive information from the running BDSS
    zmq_server = Instance(ZMQServer)

    def initialized(self):
        if self.zmq_server.state == "STOPPED":
            self.zmq_server.start()

    def prepare_destroy(self):
        self.zmq_server.stop()

    def _menu_bar_default(self):
        """A menu bar with functions relevant to the Results task.
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
                    name="Setup Workflow",
                    tooltip="Setup Workflow",
                    image=ImageResource("outline_build_black_48dp"),
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
        return GraphPane(self.analysis_m)

    def create_dock_panes(self):
        """ Creates the dock panes """
        return [self.side_pane]

    # Default initialisers

    def _side_pane_default(self):
        return ResultsPane(self.analysis_m)

    def _default_layout_default(self):
        """ Defines the default layout of the task window """
        return TaskLayout(
            left=PaneItem('force_wfmanager.results_pane'),
        )

    def _analysis_m_default(self):
        return AnalysisModel()

    @on_trait_change('window.application.run_enabled')
    def sync_run_enabled(self):
        if self.window is not None:
            self.run_enabled = self.window.application.run_enabled

    @on_trait_change('computation_running')
    def update_save_load_status(self):
        if self.window is not None:
            self.save_load_enabled = not self.computation_running

    # Menu/Toolbar Methods

    def switch_task(self):
        setup_task = self.window.get_task(
            'force_wfmanager.wfmanager_setup_task'
        )

        self.window.activate_task(setup_task)

    def exit(self):
        self.window.application.exit()

    # Default Initialisers (WfManager)

    def _executor_default(self):
        return ThreadPoolExecutor(max_workers=1)

    def _zmq_server_default(self):
        return ZMQServer(
            on_event_callback=self._server_event_callback,
            on_error_callback=self._server_error_callback
        )

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

    # BDSS Interaction

    def run_bdss(self):
        """ Run the BDSS computation """

        # Confirm we want to run a calculation
        if len(self.analysis_m.evaluation_steps) != 0:
            result = confirm(
                None,
                "Are you sure you want to run the computation and "
                "empty the result table?")
            if result is not YES:
                return

        # Get the current workflow
        setup_task = self.window.get_task(
            'force_wfmanager.wfmanager_setup_task'
        )
        self.workflow_m = setup_task.workflow_m

        # Flag that a computation is running (passed to application-level)
        self.computation_running = True
        try:
            for hook_manager in self.ui_hooks_managers:
                try:
                    hook_manager.before_execution(self)
                except Exception:
                    log.exception(
                        "Failed before_execution hook "
                        "for hook manager {}".format(
                            hook_manager.__class__.__name__)
                    )

            # Creates a temporary file containing the workflow
            tmpfile_path = tempfile.mktemp()
            with open(tmpfile_path, 'w') as output:
                WorkflowWriter().write(self.workflow_m, output)

            # Clear the analysis model before attempting to run
            self.analysis_m.clear()

            future = self.executor.submit(self._execute_bdss, tmpfile_path)
            future.add_done_callback(self._execution_done_callback)
        except Exception as e:
            logging.exception("Unable to run BDSS.")
            error(None,
                  "Unable to run BDSS: {}".format(e),
                  'Error when running BDSS'
                  )
            self.computation_running = False

    def _execute_bdss(self, workflow_path):
        """Secondary thread executor routine.
        This executes the BDSS and wait for its completion.
        """
        try:
            subprocess.check_call([self.bdss_executable_path,
                                   workflow_path])
        except OSError as e:
            log.exception("Error while executing force_bdss executable. "
                          " Is force_bdss in your path?")
            self._clean_tmp_workflow(workflow_path, silent=True)
            raise e
        except subprocess.CalledProcessError as e:
            # Ignore any error of execution.
            log.exception("force_bdss returned a "
                          "non-zero value after execution")
            self._clean_tmp_workflow(workflow_path, silent=True)
            raise e
        except Exception as e:
            log.exception("Unknown exception occurred "
                          "while invoking force bdss executable.")
            self._clean_tmp_workflow(workflow_path, silent=True)
            raise e

        self._clean_tmp_workflow(workflow_path)

    def _clean_tmp_workflow(self, workflow_path, silent=False):
        """Removes the temporary file for the workflow.

        Parameters
        ----------
        workflow_path: str
            The path of the workflow
        silent: bool
            If true, any exception encountered will be discarded (but logged).
            If false, the exception will be re-raised
        """
        try:
            os.remove(workflow_path)
        except OSError as e:
            # Ignore deletion errors, in case the file magically
            # vanished in the meantime
            log.exception("Unable to delete temporary "
                          "workflow file at {}".format(workflow_path))
            if not silent:
                raise e

    def _execution_done_callback(self, future):
        """Secondary thread code.
        Called when the execution is completed.
        """
        exc = future.exception()
        GUI.invoke_later(self._bdss_done, exc)

    def _bdss_done(self, exception):
        """Called in the main thread when the execution is completed.

        Parameters
        ----------
        exception: Exception or None
            If the execution raised an exception of any sort.
        """

        for hook_manager in self.ui_hooks_managers:
            try:
                hook_manager.after_execution(self)
            except Exception:
                log.exception(
                    "Failed after_execution hook "
                    "for hook manager {}".format(
                        hook_manager.__class__.__name__)
                )

        self.computation_running = False

        if exception is not None:
            error(
                None,
                'Execution of BDSS failed. \n\n{}'.format(
                    str(exception)),
                'Error when running BDSS'
            )

    # Plugin Status

    def open_plugins(self):
        plugins = [plugin
                   for plugin in self.plugin_manager
                   if isinstance(plugin, BaseExtensionPlugin)]

        # Plugins guaranteed to have an id, so sort by that if name is not set
        plugins.sort(key=lambda s: s.name if s.name not in ('', None)
                     else s.id)
        dlg = PluginDialog(plugins)
        dlg.edit_traits()

    # Handling of BDSS events via ZMQ server

    def _server_event_callback(self, event):
        """Callback that is called by the server thread
        when a new event is received. This method is
        executed by the server thread.
        """
        GUI.invoke_later(self._server_event_mainthread, event)

    def _server_error_callback(self, error_type, error_message):
        """Callback in case of server error. Invoked by the secondary thread"""
        if error_type == ZMQServer.ERROR_TYPE_CRITICAL:
            GUI.invoke_later(self._show_error_dialog, error_message)

    def _server_event_mainthread(self, event):
        """Invoked by the main thread.
        Handles the event received by the server, dispatching its
        action appropriately according to the type"""
        if isinstance(event, MCOStartEvent):
            self.analysis_m.clear()
            value_names = list(event.parameter_names)
            for kpi_name in event.kpi_names:
                value_names.extend([kpi_name, kpi_name+" weight"])
            self.analysis_m.value_names = tuple(value_names)
        elif isinstance(event, MCOProgressEvent):
            data = [dv.value for dv in event.optimal_point]
            for kpi, weight in zip(event.optimal_kpis, event.weights):
                data.extend([kpi.value, weight])

            data = tuple(map(float, data))
            self.analysis_m.add_evaluation_step(data)

    # Error Display

    def _show_error_dialog(self, message):
        """Shows an error dialog to the user with a given message"""
        error(None, message, "Server error")