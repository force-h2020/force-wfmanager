import logging
import os
import subprocess
import tempfile
import textwrap

from concurrent.futures import ThreadPoolExecutor

from envisage.ui.tasks.api import TasksApplication, TaskWindow

from pyface.api import (CANCEL, confirm, ConfirmationDialog, error, FileDialog,
                        GUI, information, NO, OK, YES)
from pyface.tasks.api import TaskWindowLayout, Task

from traits.api import Bool, File, Instance, List, Unicode

from force_bdss.api import (
    MCOProgressEvent, MCOStartEvent, BaseUIHooksManager, Workflow,
    IFactoryRegistryPlugin, WorkflowReader, WorkflowWriter,
    InvalidFileException, BaseExtensionPlugin, FACTORY_REGISTRY_PLUGIN_ID)

from force_wfmanager.wfmanager_plugin import WfManagerPlugin
from force_wfmanager.plugin_dialog import PluginDialog
from force_wfmanager.server.zmq_server import ZMQServer
from force_wfmanager.central_pane.analysis_model import AnalysisModel

log = logging.getLogger(__name__)


class WfManager(TasksApplication):
    id = 'force_wfmanager.wfmanager'
    name = 'Workflow Manager'

    #: Workflow model.
    workflow_m = Instance(Workflow, allow_none=False)

    #: Analysis model. Contains the results that are displayed in the plot
    #: and table
    analysis_m = Instance(AnalysisModel, allow_none=False)

    #: Registry of the available factories
    factory_registry = Instance(IFactoryRegistryPlugin)

    #: The tasks belonging to this application
    tasks = List(Instance(Task))

    #: Current workflow file on which the application is writing
    current_file = File()

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

    #: Flag which says if the computation is running or not
    computation_running = Bool(False)

    #: Flag indicating if the current workflow is ready to run
    run_enabled = Bool(True)

    def __init__(self, plugins, workflow_file):
        super(WfManager, self).__init__(plugins=plugins)
        if workflow_file is not None:
            self.open_workflow_file(workflow_file)
        # Things to be shared between both the tasks. In order to keep this
        # link, the objects in the tasks should react to trait changes at
        # the application level.
        shared_items = {
            'analysis_m': self.analysis_m,
            'workflow_m': self.workflow_m,
            'factory_registry': self.factory_registry,
                        }
        wfmanager_plugin = WfManagerPlugin(shared_items)
        self.add_plugin(wfmanager_plugin)

    def _factory_registry_default(self):
        """The envisage plugin containing all of the mco, datasource and
        notification listener factories defined in external (non-envisage!)
        plugins"""
        factory_registry = self.get_plugin(FACTORY_REGISTRY_PLUGIN_ID)
        return factory_registry

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

    def run_bdss(self):
        """ Run the BDSS computation """
        if len(self.analysis_m.evaluation_steps) != 0:
            result = confirm(
                None,
                "Are you sure you want to run the computation and "
                "empty the result table?")
            if result is not YES:
                return

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

    def _workflow_m_default(self):
        return Workflow()

    def _analysis_m_default(self):
        return AnalysisModel()

    def _executor_default(self):
        return ThreadPoolExecutor(max_workers=1)

    def _zmq_server_default(self):
        return ZMQServer(
            on_event_callback=self._server_event_callback,
            on_error_callback=self._server_error_callback
        )

    def _tasks_default(self):
        tasks = []
        for window in self.windows:
            tasks.extend(window.tasks)
        return tasks

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

    def open_plugins(self):
        plugins = [plugin
                   for plugin in self.plugin_manager
                   if isinstance(plugin, BaseExtensionPlugin)]

        # Plugins guaranteed to have an id, so sort by that if name is not set
        plugins.sort(key=lambda s: s.name if s.name not in ('', None)
                     else s.id)
        dlg = PluginDialog(plugins)
        dlg.edit_traits()

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
            print(self.analysis_m.value_names,
                  self.analysis_m.evaluation_steps)
        elif isinstance(event, MCOProgressEvent):
            data = [dv.value for dv in event.optimal_point]
            for kpi, weight in zip(event.optimal_kpis, event.weights):
                data.extend([kpi.value, weight])

            data = tuple(map(float, data))
            self.analysis_m.add_evaluation_step(data)
            print(self.analysis_m.value_names,
                  self.analysis_m.evaluation_steps)

    def _show_error_dialog(self, message):
        """Shows an error dialog to the user with a given message"""
        error(None, message, "Server error")

    def _default_layout_default(self):
        tasks = [factory.id for factory in self.task_factories]
        return [TaskWindowLayout(
            *tasks,
            active_task='force_wfmanager.wfmanager_setup_task',
            size=(800, 600)
        )]

    def _window_factory_default(self):
        """Sets a TaskWindow with closing prompt to be the default window
        created by TasksApplication (originally a standard TaskWindow)"""
        return TaskWindowClosePrompt

    # FIXME: This isn't needed if the bug in traitsui/qt4/ui_panel.py is fixed
    def _prepare_exit(self):
        """Same functionality as TasksApplication._prepare_exit(), but
        _save_state is called before application_exiting is fired"""
        self._save_state()
        self.application_exiting = self

    def _application_initialized_fired(self):
        self.zmq_server.start()

    # FIXME: This isn't needed if the bug in traitsui/qt4/ui_panel.py is fixed
    def _application_exiting_fired(self):
        self.zmq_server.stop()
        self._remove_tasks()

    def _remove_tasks(self):
        """Removes the task elements from all windows in the application.
        Part of a workaround for a bug in traitsui/qt4/ui_panel.py where
        sizeHint() would be called, even when a Widget was already destroyed"""
        for window in self.windows:
            tasks = window.tasks
            for task in tasks:
                window.remove_task(task)


class TaskWindowClosePrompt(TaskWindow):
    """A TaskWindow which asks if you want to save before closing"""

    def close(self):
        """ Closes the window. It first asks the user to
        save the current Workflow. The user can accept to save, ignore the
        request, or cancel the quit. If the user wants to save, but the save
        fails, the application is not closed so he has a chance to try to
        save again. Overrides close from pyface.tasks.task_window """

        # The attached wfmanager_task for saving methods
        wfmanager = self.application

        # Pop up for user input
        dialog = ConfirmationDialog(
            parent=None,
            message='Do you want to save before exiting the Workflow '
                    'Manager ?',
            cancel=True,
            yes_label='Save',
            no_label='Don\'t save',
        )
        result = dialog.open()

        # Save
        if result is YES:
            save_result = wfmanager.save_workflow()

            # On a failed save, don't close the window
            if not save_result:
                return False

            close_result = super(TaskWindowClosePrompt, self).close()
            return close_result

        # Don't save
        elif result is NO:
            close_result = super(TaskWindowClosePrompt, self).close()
            return close_result

        # Cancel
        elif result is CANCEL:
            return False
