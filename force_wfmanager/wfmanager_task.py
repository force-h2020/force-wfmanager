import subprocess

import tempfile
from contextlib import contextmanager
import logging
import os

from traits.api import Instance, on_trait_change, File

from pyface.tasks.api import Task, TaskLayout, PaneItem, Splitter
from pyface.tasks.action.api import SMenu, SMenuBar, TaskAction
from pyface.api import FileDialog, OK, error

from force_bdss.factory_registry_plugin import FactoryRegistryPlugin
from force_bdss.core.workflow import Workflow
from force_bdss.io.workflow_writer import WorkflowWriter
from force_bdss.io.workflow_reader import WorkflowReader, InvalidFileException

from force_wfmanager.central_pane.central_pane import CentralPane
from force_wfmanager.left_side_pane.workflow_settings import WorkflowSettings
from force_wfmanager.left_side_pane.bdss_runner import BDSSRunner


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

    #: WorkflowSettings pane, it displays the workflow in a tree editor and
    #: allows to edit it
    workflow_settings = Instance(WorkflowSettings, allow_none=False)

    #: The pane containing the run button for running the BDSS
    bdss_runner = Instance(BDSSRunner, allow_none=False)

    #: Registry of the available factories
    factory_registry = Instance(FactoryRegistryPlugin)

    #: Current workflow file on which the application is writing
    current_file = File()

    #: Menu bar on top of the GUI
    menu_bar = SMenuBar(SMenu(
        TaskAction(
            name='Save Workflow...',
            method='save_workflow',
            accelerator='Ctrl+S',
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
        """ Creates the dock panes which contains the MCO, datasources and
        Constraints management """
        return [
            self.workflow_settings,
            self.bdss_runner
        ]

    def save_workflow(self):
        """ Shows a dialog to save the workflow into a JSON file """
        writer = WorkflowWriter()

        # If the user already saved before or loaded a file, we overwrite this
        # file
        if len(self.current_file) != 0:
            current_file = self.current_file
        else:
            dialog = FileDialog(
                action="save as", default_filename="workflow.json")
            result = dialog.open()

            if result is not OK:
                return

            current_file = dialog.path

        with open(current_file, 'w') as output:
            writer.write(self.workflow_m, output)
            self.current_file = current_file

    def load_workflow(self):
        """ Shows a dialog to load a workflow file """
        dialog = FileDialog(action="open")
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

    @on_trait_change('bdss_runner.run_button')
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
            left=Splitter(
                PaneItem('force_wfmanager.workflow_settings'),
                PaneItem('force_wfmanager.bdss_runner'),
                orientation='vertical'
            )
        )

    def _workflow_m_default(self):
        return Workflow()

    def _bdss_runner_default(self):
        return BDSSRunner()

    def _workflow_settings_default(self):
        registry = self.factory_registry
        kpi_calculator_factories = registry.kpi_calculator_factories
        return WorkflowSettings(
            available_mco_factories=registry.mco_factories,
            available_data_source_factories=registry.data_source_factories,
            available_kpi_calculator_factories=kpi_calculator_factories,
            workflow_m=self.workflow_m)

    @on_trait_change('workflow_m')
    def update_workflow_settings(self):
        self.workflow_settings.workflow_m = self.workflow_m
