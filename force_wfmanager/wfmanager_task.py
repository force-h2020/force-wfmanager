import subprocess
import logging

import tempfile
import os
from concurrent.futures import ThreadPoolExecutor

from traits.api import Instance, on_trait_change, File

from pyface.tasks.api import Task, TaskLayout, PaneItem
from pyface.tasks.action.api import SMenu, SMenuBar, TaskAction
from pyface.api import FileDialog, OK, error, GUI

from force_bdss.factory_registry_plugin import FactoryRegistryPlugin
from force_bdss.core.workflow import Workflow
from force_bdss.io.workflow_writer import WorkflowWriter
from force_bdss.io.workflow_reader import WorkflowReader, InvalidFileException

from force_wfmanager.central_pane.central_pane import CentralPane
from force_wfmanager.left_side_pane.side_pane import SidePane


log = logging.getLogger(__name__)


class WfManagerTask(Task):
    id = 'force_wfmanager.wfmanager_task'
    name = 'Workflow Manager'

    #: Workflow model
    workflow_m = Instance(Workflow, allow_none=False)

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
    _bdss_executable_path = "force_bdss"

    #: Menu bar on top of the GUI
    menu_bar = SMenuBar(SMenu(
        TaskAction(
            name='Save Workflow...',
            method='save_workflow',
            accelerator='Ctrl+S',
        ),
        TaskAction(
            name='Open Workflow...',
            method='open_workflow',
            accelerator='Ctrl+O',
        ), id='File', name='&File'
    ))

    def create_central_pane(self):
        """ Creates the central pane which contains the analysis part
        (pareto front and output KPI values)
        """
        return CentralPane()

    def create_dock_panes(self):
        """ Creates the dock panes """
        return [self.side_pane]

    def save_workflow(self):
        """ Shows a dialog to save the workflow into a JSON file """
        writer = WorkflowWriter()

        # If the user already saved before or loaded a file, we overwrite this
        # file
        if len(self.current_file) != 0:
            current_file = self.current_file
        else:
            dialog = FileDialog(
                action="save as",
                default_filename="workflow.json",
                wildcard='JSON files (*.json)|*.json|'
            )
            result = dialog.open()

            if result is not OK:
                return

            current_file = dialog.path

        try:
            with open(current_file, 'w') as output:
                writer.write(self.workflow_m, output)
                self.current_file = current_file
        except IOError as e:
            error(
                None,
                'Cannot save in the requested file:\n\n{}'.format(
                    str(e)),
                'Error when saving workflow'
            )

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

    @on_trait_change('side_pane.run_button')
    def run_bdss(self):
        """ Run the BDSS computation """
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

    # Default initializers

    def _default_layout_default(self):
        """ Defines the default layout of the task window """
        return TaskLayout(
            left=PaneItem('force_wfmanager.side_pane')
        )

    def _workflow_m_default(self):
        return Workflow()

    def _side_pane_default(self):
        return SidePane(
            factory_registry=self.factory_registry,
            workflow_m=self.workflow_m
        )

    def __executor_default(self):
        return ThreadPoolExecutor(max_workers=1)

    # Handlers

    @on_trait_change('workflow_m')
    def update_side_pane(self):
        self.side_pane.workflow_m = self.workflow_m
