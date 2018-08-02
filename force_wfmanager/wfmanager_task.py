import logging
import os
import subprocess
import tempfile
import textwrap

from concurrent.futures import ThreadPoolExecutor

from traits.api import Instance, on_trait_change, File, Unicode, Bool, List

from pyface.api import (
    FileDialog, OK, error, ConfirmationDialog, YES, CANCEL, GUI, confirm,
    information
)

from pyface.tasks.action.api import SMenu, SMenuBar, TaskAction
from pyface.tasks.api import Task, TaskLayout, PaneItem

from force_bdss.api import (
    MCOProgressEvent, MCOStartEvent, BaseUIHooksManager, Workflow,
    IFactoryRegistryPlugin, WorkflowReader, WorkflowWriter,
    InvalidFileException, BaseExtensionPlugin)

from force_wfmanager.central_pane.analysis_model import AnalysisModel
from force_wfmanager.central_pane.central_pane import CentralPane
from force_wfmanager.left_side_pane.side_pane import SidePane
from force_wfmanager.plugin_dialog import PluginDialog
from force_wfmanager.server.zmq_server import ZMQServer

log = logging.getLogger(__name__)


class WfManagerTask(Task):
    id = 'force_wfmanager.wfmanager_task'
    name = 'Workflow Manager'

    #: Workflow model.
    workflow_m = Instance(Workflow, allow_none=False)

    #: Analysis model. Contains the results that are displayed in the plot
    #: and table
    analysis_m = Instance(AnalysisModel, allow_none=False)

    #: Side Pane containing the tree editor for the Workflow and the Run button
    side_pane = Instance(SidePane)

    #: Registry of the available factories
    factory_registry = Instance(IFactoryRegistryPlugin)

    #: Current workflow file on which the application is writing
    current_file = File()

    #: A list of UI hooks managers. These hold plugin injected "hook managers",
    #: classes with methods that are called when some operation is performed
    #: by the UI
    _ui_hooks_managers = List(BaseUIHooksManager)

    #: The thread pool executor to spawn the BDSS CLI process.
    _executor = Instance(ThreadPoolExecutor)

    #: Path to spawn for the BDSS CLI executable.
    #: This will go to some global configuration option later.
    _bdss_executable_path = Unicode("force_bdss")

    #: ZeroMQ Server to receive information from the running BDSS
    zmq_server = Instance(ZMQServer)

    #: Flag which says if the computation is running or not
    _computation_running = Bool(False)

    #: Flag which says if the menus should be disabled or not
    _menu_enabled = Bool(True)

    #: Menu bar on top of the GUI
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
                enabled_name='_menu_enabled',
                accelerator='Ctrl+O',
            ),
            TaskAction(
                name='Save Workflow',
                method='save_workflow',
                enabled_name='_menu_enabled',
                accelerator='Ctrl+S',
            ),
            TaskAction(
                name='Save Workflow as...',
                method='save_workflow_as',
                enabled_name='_menu_enabled',
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
    )

    def create_central_pane(self):
        """ Creates the central pane which contains the analysis part
        (pareto front and output KPI values)
        """
        return CentralPane(self.analysis_m)

    def create_dock_panes(self):
        """ Creates the dock panes """
        return [self.side_pane]

    def initialized(self):
        self.zmq_server.start()

    def prepare_destroy(self):
        self.zmq_server.stop()

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
        for hook_manager in self._ui_hooks_managers:
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

    @on_trait_change('_computation_running')
    def update_side_pane_status(self):
        self.side_pane.ui_enabled = not self._computation_running
        self._menu_enabled = not self._computation_running

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

    def open_plugins(self):
        plugins = [plugin
                   for plugin in self.window.application.plugin_manager
                   if isinstance(plugin, BaseExtensionPlugin)]

        # Plugins guaranteed to have an id, so sort by that if name is not set
        plugins.sort(key=lambda s: s.name if s.name not in ('', None)
                     else s.id)
        dlg = PluginDialog(plugins)
        dlg.edit_traits()

    @on_trait_change('side_pane.run_button')
    def run_bdss(self):
        """ Run the BDSS computation """
        if len(self.analysis_m.evaluation_steps) != 0:
            result = confirm(
                None,
                "Are you sure you want to run the computation and "
                "empty the result table?")
            if result is not YES:
                return

        self._computation_running = True
        try:
            for hook_manager in self._ui_hooks_managers:
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

            future = self._executor.submit(self._execute_bdss, tmpfile_path)
            future.add_done_callback(self._execution_done_callback)
        except Exception as e:
            logging.exception("Unable to run BDSS.")
            error(None,
                  "Unable to run BDSS: {}".format(e),
                  'Error when running BDSS'
                  )
            self._computation_running = False

    def _execute_bdss(self, workflow_path):
        """Secondary thread executor routine.
        This executes the BDSS and wait for its completion.
        """
        try:
            subprocess.check_call([self._bdss_executable_path, workflow_path])
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

        for hook_manager in self._ui_hooks_managers:
            try:
                hook_manager.after_execution(self)
            except Exception:
                log.exception(
                    "Failed after_execution hook "
                    "for hook manager {}".format(
                        hook_manager.__class__.__name__)
                )

        self._computation_running = False

        if exception is not None:
            error(
                None,
                'Execution of BDSS failed. \n\n{}'.format(
                    str(exception)),
                'Error when running BDSS'
            )

    def exit(self):
        """ Exit the application. It first asks the user to save the current
        Worklfow. The user can accept to save, ignore the request, or
        cancel the quit. If the user wants to save, but the save fails, the
        application is not closed so he has a chance to try to save again. """
        dialog = ConfirmationDialog(
            parent=None,
            message='Do you want to save before exiting the Workflow '
                    'Manager ?',
            cancel=True,
            yes_label='Save',
            no_label='Don\'t save',
        )

        result = dialog.open()

        if result is YES:
            save_result = self.save_workflow()
            if not save_result:
                return
        elif result is CANCEL:
            return

        app = self.window.application
        app.exit()

    # Default initializers

    def _default_layout_default(self):
        """ Defines the default layout of the task window """
        return TaskLayout(
            left=PaneItem('force_wfmanager.side_pane')
        )

    def _workflow_m_default(self):
        return Workflow()

    def _analysis_m_default(self):
        return AnalysisModel()

    def _side_pane_default(self):
        return SidePane(
            factory_registry=self.factory_registry,
            workflow_m=self.workflow_m
        )

    def __executor_default(self):
        return ThreadPoolExecutor(max_workers=1)

    def _zmq_server_default(self):
        return ZMQServer(
            on_event_callback=self._server_event_callback,
            on_error_callback=self._server_error_callback
        )

    def __ui_hooks_managers_default(self):
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

    # Handlers

    @on_trait_change('workflow_m')
    def update_side_pane(self):
        self.side_pane.workflow_m = self.workflow_m

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

    def _show_error_dialog(self, message):
        """Shows an error dialog to the user with a given message"""
        error(None, message, "Server error")
