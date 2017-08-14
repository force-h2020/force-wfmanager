import subprocess

import tempfile
from contextlib import contextmanager
import logging
import os

from traits.api import Instance, on_trait_change, File

from pyface.tasks.api import Task, TaskLayout, PaneItem
from pyface.tasks.action.api import SMenu, SMenuBar, TaskAction
from pyface.api import FileDialog, OK, error

from force_bdss.factory_registry_plugin import FactoryRegistryPlugin
from force_bdss.core.workflow import Workflow
from force_bdss.io.workflow_writer import WorkflowWriter
from force_bdss.io.workflow_reader import WorkflowReader, InvalidFileException

from force_wfmanager.central_pane.central_pane import CentralPane
from force_wfmanager.left_side_pane.side_pane import SidePane


@contextmanager
def cleanup_garbage(tmpfile):
    yield

    try:
        os.remove(tmpfile)
    except OSError:
        logging.exception("Could not delete the tmp file {}".format(tmpfile))
        raise


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

    #: Menu bar on top of the GUI
    menu_bar = SMenuBar(SMenu(
        TaskAction(
            name='Save Workflow',
            method='save_workflow',
            accelerator='Ctrl+S',
            enabled_name='current_file',
        ),
        TaskAction(
            name='Save Workflow as...',
            method='save_workflow_as',
            accelerator='Shift+Ctrl+S',
        ),
        TaskAction(
            name='Load Workflow...',
            method='load_workflow',
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
        if len(self.current_file) == 0:
            return

        self._write_workflow(self.current_file)

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

        if self._write_workflow(current_file) is True:
            self.current_file = current_file

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
        writer = WorkflowWriter()
        try:
            with open(file_path, 'w') as output:
                writer.write(self.workflow_m, output)
        except IOError as e:
            error(
                None,
                'Cannot save in the requested file:\n\n{}'.format(
                    str(e)),
                'Error when saving workflow'
            )
            return False
        else:
            return True

    def load_workflow(self):
        """ Shows a dialog to load a workflow file """
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
        tmpfile = tempfile.mkstemp()
        tmpfile_path = tmpfile[1]

        with cleanup_garbage(tmpfile_path):
            # Creates a temporary file containing the workflow
            with open(tmpfile_path, 'w') as output:
                WorkflowWriter().write(self.workflow_m, output)

            # Starts the bdss
            subprocess.check_call(["force_bdss", tmpfile_path])

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

    @on_trait_change('workflow_m')
    def update_side_pane(self):
        self.side_pane.workflow_m = self.workflow_m
