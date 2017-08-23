import logging
import os
import subprocess
import tempfile
import textwrap

from concurrent.futures import ThreadPoolExecutor
from pyface.api import (
    FileDialog, OK, error, ConfirmationDialog, YES, CANCEL, GUI, confirm,
    information
)

from pyface.tasks.action.api import SMenu, SMenuBar, TaskAction
from pyface.tasks.api import Task, TaskLayout, PaneItem
from traits.api import Instance, on_trait_change, File, Str

from force_bdss.api import MCOProgressEvent, MCOStartEvent
from force_bdss.core.workflow import Workflow
from force_bdss.factory_registry_plugin import FactoryRegistryPlugin
from force_bdss.io.workflow_reader import WorkflowReader, InvalidFileException
from force_bdss.io.workflow_writer import WorkflowWriter
from force_wfmanager.central_pane.analysis_model import AnalysisModel
from force_wfmanager.central_pane.central_pane import CentralPane
from force_wfmanager.left_side_pane.side_pane import SidePane
from force_wfmanager.server.zmq_server import ZMQServer
from force_wfmanager.server.zmq_server_config import ZMQServerConfig

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
    factory_registry = Instance(FactoryRegistryPlugin)

    #: Current workflow file on which the application is writing
    current_file = File()

    #: The thread pool executor to spawn the BDSS CLI process.
    _executor = Instance(ThreadPoolExecutor)

    #: Path to spawn for the BDSS CLI executable.
    #: This will go to some global configuration option later.
    _bdss_executable_path = Str("force_bdss")

    #: ZeroMQ Server to receive information from the running BDSS
    _zmq_server = Instance(ZMQServer)

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
                accelerator='Ctrl+O',
            ),
            TaskAction(
                name='Save Workflow',
                method='save_workflow',
                accelerator='Ctrl+S',
            ),
            TaskAction(
                name='Save Workflow as...',
                method='save_workflow_as',
                accelerator='Shift+Ctrl+S',
            ),
            name='&File'
        ),
        SMenu(
            TaskAction(
                name='About WorflowManager...',
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
        self._zmq_server.start()

    def prepare_destroy(self):
        self._zmq_server.stop()

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
        file_path: String
            The file_path pointing to the file in which you want to write the
            workflow

        Returns
        -------
        Boolean:
            True if it was a success to write in the file, False otherwise
        """
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

        if result is OK:
            reader = WorkflowReader(self.factory_registry)
            try:
                with open(dialog.path, 'r') as fobj:
                    self.workflow_m = reader.read(fobj)
            except InvalidFileException as e:
                error(
                    None,
                    'Cannot read the requested file:\n\n{}'.format(
                        str(e)),
                    'Error when reading file'
                )
            else:
                self.current_file = dialog.path

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
            "About WorflowManager"
        )

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

        tmpfile_path = tempfile.mktemp()

        # Creates a temporary file containing the workflow
        try:
            with open(tmpfile_path, 'w') as output:
                WorkflowWriter().write(self.workflow_m, output)
        except Exception as e:
            logging.exception("Unable to create temporary workflow file.")
            error(None,
                  "Unable to create temporary workflow file for execution "
                  "of the BDSS. {}".format(e),
                  'Error when saving workflow'
                  )
            return

        self.side_pane.enabled = False
        future = self._executor.submit(self._execute_bdss, tmpfile_path)
        future.add_done_callback(self._execution_done_callback)

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
        self.side_pane.enabled = True
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

        self.window.application.exit()

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

    def __zmq_server_default(self):
        config = ZMQServerConfig()
        return ZMQServer(config, on_event_callback=self._server_event_callback)

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

    def _server_event_mainthread(self, event):
        """Invoked by the main thread.
        Handles the event received by the server, dispatching its
        action appropriately according to the type"""
        if isinstance(event, MCOStartEvent):
            self.analysis_m.clear()
            self.analysis_m.value_names = (
                event.input_names + event.output_names)
        elif isinstance(event, MCOProgressEvent):
            data = tuple(map(float, event.input + event.output))
            self.analysis_m.add_evaluation_step(data)
