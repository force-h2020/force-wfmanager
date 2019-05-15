from concurrent.futures import ThreadPoolExecutor
import os
import logging
import subprocess
import tempfile
import textwrap

from pyface.api import (
    FileDialog, GUI, ImageResource, OK, YES, confirm, error, information
)
from pyface.tasks.action.api import SMenu, SMenuBar, SToolBar, TaskAction
from pyface.tasks.api import PaneItem, Task, TaskLayout
from traits.api import Instance, on_trait_change, List, Bool, Unicode, File

from force_bdss.api import (
    BaseExtensionPlugin, BaseUIHooksManager, IFactoryRegistry,
    InvalidFileException, MCOProgressEvent, MCOStartEvent, Workflow,
    WorkflowReader, WorkflowWriter
)
from force_wfmanager.central_pane.analysis_model import AnalysisModel
from force_wfmanager.central_pane.setup_pane import SetupPane
from force_wfmanager.central_pane.data_view_pane import DataViewPane
from force_wfmanager.plugin_dialog import PluginDialog
from force_wfmanager.left_side_pane.tree_pane import TreePane
from force_wfmanager.server.zmq_server import ZMQServer
from force_wfmanager.task_toggle_group_accelerator import (
    TaskToggleGroupAccelerator
)

log = logging.getLogger(__name__)


class WfManagerSetupTask(Task):
    id = 'force_wfmanager.wfmanager_setup_task'
    name = 'Workflow Setup'

    #: Workflow model.
    workflow_model = Instance(Workflow, allow_none=False)

    #: Analysis model. Contains the results that are displayed in the plot
    #: and table
    analysis_model = Instance(AnalysisModel, allow_none=False)

    #: Registry of the available factories
    factory_registry = Instance(IFactoryRegistry)

    #: Current workflow file on which the application is writing
    current_file = File()

    #: Side Pane containing the tree editor for the Workflow and the Run button
    side_pane = Instance(TreePane)

    #: The menu bar for this task.
    menu_bar = Instance(SMenuBar)

    #: The tool bars for this task.
    tool_bars = List(SToolBar)

    #: Indicates whether the 'run' toolbar and side pane buttons are active
    run_enabled = Bool(True)

    #: Indicates whether the saving and loading menu/toolbar buttons are
    #: active.
    save_load_enabled = Bool(True)

    #: Indicates whether there a bdss computation running
    computation_running = Bool(False)

    #: The thread pool executor to spawn the BDSS CLI process.
    executor = Instance(ThreadPoolExecutor)

    selected_data_view = Instance(type)

    plugin_data_views = List

    #: Path to spawn for the BDSS CLI executable.
    #: This will go to some global configuration option later.
    bdss_executable_path = Unicode("force_bdss")

    #: ZeroMQ Server to receive information from the running BDSS
    zmq_server = Instance(ZMQServer)

    #: A list of UI hooks managers. These hold plugin injected "hook managers",
    #: classes with methods that are called when some operation is performed
    #: by the UI
    ui_hooks_managers = List(BaseUIHooksManager)

    task_group = Instance(TaskToggleGroupAccelerator)

    #: Results Task
    results_task = Instance(Task)

    # ZMQ Setup

    def initialized(self):
        """Overrides method from Task. Starts the ZMQ Server when this Task is
        initialized
        """
        self.zmq_server.start()

    def prepare_destroy(self):
        """Overrides method from Task. Stops the ZMQ Server when this Task is
        about to be destroyed
        """
        self.zmq_server.stop()

    # Task Defaults and Initialisers

    def _menu_bar_default(self):
        """A menu bar with functions relevant to the Setup task.
        """
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
                TaskAction(
                    name='Exit',
                    method='exit',
                ),

                # NOTE: Setting id='File' here will automatically create
                #       a exit menu item, I guess this is QT being 'helpful'.
                #       This menu item calls application.exit, which bypasses
                #       our custom exit which prompts for a save before exiting
                name='&File',

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

    def _default_layout_default(self):
        """ Defines the default layout of the task window """
        return TaskLayout(
            left=PaneItem('force_wfmanager.tree_pane'),
        )

    def create_central_pane(self):
        """ Creates the central pane which contains the analysis part
        (pareto front and output KPI values)
        """
        return SetupPane(workflow_model=self.workflow_model)

    def create_dock_panes(self):
        """ Creates the dock panes """
        return [self.side_pane]

    # Default initializers

    def _side_pane_default(self):
        return TreePane(
            factory_registry=self.factory_registry,
            workflow_model=self.workflow_model,
            plugin_data_views=self.plugin_data_views
        )

    def _workflow_model_default(self):
        return Workflow()

    def _analysis_model_default(self):
        return AnalysisModel()

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

    def _executor_default(self):
        return ThreadPoolExecutor(max_workers=1)

    def _zmq_server_default(self):
        return ZMQServer(
            on_event_callback=self._server_event_callback,
            on_error_callback=self._server_error_callback
        )

    # Workflow Methods

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

    def open_workflow_file(self, f_name):
        """ Opens a workflow from the specified file name

        Parameters
        ----------
        f_name: str
            The path to the workflow file
        """
        reader = WorkflowReader(self.factory_registry)
        try:
            with open(f_name, 'r') as fobj:
                self.workflow_model = reader.read(fobj)
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
                WorkflowWriter().write(self.workflow_model, output)
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

    def open_about(self):
        """Opens an information dialog"""
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

    # BDSS Interaction

    def run_bdss(self):
        """ Run the BDSS computation """

        # Confirm we want to run a calculation
        if len(self.analysis_model.evaluation_steps) != 0:
            result = confirm(
                None,
                "Are you sure you want to run the computation and "
                "empty the result table?")
            if result is not YES:
                return

        # Flag that a computation is running
        self.computation_running = True
        # Run any plugin injected ui hooks before execution
        # For example, the UI Notification Hooks Manager sets up sockets
        # to communicate with the server before executing a workflow
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
                WorkflowWriter().write(self.workflow_model, output)

            # Clear the analysis model before attempting to run
            self.analysis_model.clear()

            # Execute the bdss on a different thread
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
        """Opens a dialogue window displaying information about the currently
        loaded plugins
        """
        plugins = [plugin
                   for plugin in self.window.application.plugin_manager
                   if isinstance(plugin, BaseExtensionPlugin)]

        # Plugins guaranteed to have an id, so sort by that if name is not set
        plugins.sort(key=lambda s: s.name
                     if s.name not in ('', None) else s.id)
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
            self.analysis_model.clear()
            value_names = list(event.parameter_names)
            for kpi_name in event.kpi_names:
                value_names.extend([kpi_name, kpi_name + " weight"])
            self.analysis_model.value_names = tuple(value_names)
        elif isinstance(event, MCOProgressEvent):
            data = [dv.value for dv in event.optimal_point]
            for kpi, weight in zip(event.optimal_kpis, event.weights):
                data.extend([kpi.value, weight])
            for i, data_val in enumerate(data[:]):
                try:
                    data[i] = float(data_val)
                except ValueError:
                    data[i] = str(data_val)

            self.analysis_model.add_evaluation_step(data)

    # Error Display

    def _show_error_dialog(self, message):
        """Shows an error dialog to the user with a given message"""
        error(None, message, "Server error")

    # Synchronization with side pane (Tree Pane)

    @on_trait_change('side_pane.run_enabled')
    def set_toolbar_run_btn_state(self):
        """ Sets the run button to be enabled/disabled, matching the
        value of :attr:`side_pane.run_enabled
        <.left_side_pane.tree_pane.TreePane.run_enabled>`
        """
        self.run_enabled = self.side_pane.run_enabled

    @on_trait_change('workflow_model')
    def update_side_pane_model(self):
        """ Updates the local :attr:`workflow_model`, to match
        :attr:`side_pane.workflow_model
        <.left_side_pane.tree_pane.TreePane.workflow_model>`, which will
        change as the user modifies a workflow via the UI."""
        self.side_pane.workflow_model = self.workflow_model

    @on_trait_change('computation_running')
    def update_pane_active_status(self):
        """Disables the saving/loading toolbar buttons and the TreePane UI
        if a computation is running, and re-enables them when it finishes."""

        self.side_pane.ui_enabled = not self.computation_running
        self.save_load_enabled = not self.computation_running
        self.run_enabled = not self.computation_running

    # Method call from side pane interaction

    @on_trait_change('side_pane.run_button')
    def run_button_clicked(self):
        """ Calls :func:`run_bdss` and runs the BDSS!"""
        self.run_bdss()

    # Synchronization with Window

    @on_trait_change('window.tasks')
    def get_results_task(self):
        if self.window is not None:
            for task in self.window.tasks:
                if task.name == "Results":
                    self.results_task = task
                    self.results_task.run_enabled = self.run_enabled

    def _plugin_data_views_default(self):
        plugin_data_views = [DataViewPane]
        for plugin in self.window.application.plugin_manager:
            try:
                if plugin.data_views:
                    plugin_data_views.extend(plugin.data_views)
            except Exception:
                pass
        return plugin_data_views

    @on_trait_change('side_pane.selected_data_view')
    def _set_selected_data_view(self):
        self.selected_data_view = self.side_pane.selected_data_view

    def _selected_data_view_default(self):
        # This should always fallback to the default DataViewPane.
        return self._plugin_data_views_default()[0]

    # Menu/Toolbar Methods

    def switch_task(self):
        """Switches to the results task and verifies startup setting are
        correct for toolbars/menus etc."""
        self.window.activate_task(self.results_task)

    def exit(self):
        self.window.close()
