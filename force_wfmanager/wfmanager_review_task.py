import logging
import tempfile
import copy

from pyface.api import ImageResource, FileDialog, OK, error
from pyface.tasks.action.api import SMenuBar, SMenu, TaskAction, SToolBar
from pyface.tasks.api import Task, TaskLayout, PaneItem
from traits.api import Bool, Instance, List, on_trait_change

from force_bdss.api import Workflow, WorkflowWriter, WorkflowReader

from force_wfmanager.model.analysis_model import AnalysisModel
from force_wfmanager.ui.review.data_view_pane import DataViewPane
from force_wfmanager.ui.review.results_pane import ResultsPane
from force_wfmanager.wfmanager import (
    TaskToggleGroupAccelerator
)
from force_wfmanager.io.analysis_model_io import write_analysis_model
from force_wfmanager.io.project_io import write_project_file, load_project_file

log = logging.getLogger(__name__)


class WfManagerReviewTask(Task):
    """Task responsible for running the Workflow and displaying the results."""

    #: Top pane containing the analysis in table form
    side_pane = Instance(ResultsPane)

    #: Main pane containing the graphs
    central_pane = Instance(DataViewPane)

    #: The menu bar for this task.
    menu_bar = Instance(SMenuBar)

    #: The tool bars for this task.
    tool_bars = List(SToolBar)

    id = 'force_wfmanager.wfmanager_review_task'

    name = 'Review'

    #: Workflow model used to create the review in the analysis model.
    #: This trait no longer tracks the workflow stored under
    #: :attr:`setup_task.workflow_model` and instead is only updated
    #: when a new run is started.
    workflow_model = Instance(Workflow)

    #: Analysis model. Contains the results that are displayed in the plot
    #: and table
    analysis_model = Instance(AnalysisModel, allow_none=False)

    #: Is the 'run' toolbar button active
    run_enabled = Bool(True)

    #: Are the saving and loading menu/toolbar buttons active
    save_load_enabled = Bool(True)

    #: Is the results saving button enabled, i.e. are there results?
    export_results_enabled = Bool(False)

    #: Setup Task
    setup_task = Instance(Task)

    def _menu_bar_default(self):
        """A menu bar with functions relevant to the Review task.
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
                    method='setup_task.open_workflow',
                    enabled_name='save_load_enabled',
                    accelerator='Ctrl+O',
                ),
                TaskAction(
                    name='Save Workflow',
                    method='setup_task.save_workflow',
                    enabled_name='save_load_enabled',
                    accelerator='Ctrl+S',
                ),
                TaskAction(
                    name='Save Workflow as...',
                    method='setup_task.save_workflow_as',
                    enabled_name='save_load_enabled',
                    accelerator='Shift+Ctrl+S',
                ),
                TaskAction(
                    name='Save Results as...',
                    method='export_analysis_model_as',
                    enabled_name='export_results_enabled'
                ),
                TaskAction(
                    name='Plugins...',
                    method='setup_task.open_plugins'
                ),
                TaskAction(
                    name='Exit',
                    method='exit',
                ),
                name='&File'
            ),
            SMenu(
                TaskAction(
                    name='About WorkflowManager...',
                    method='setup_task.open_about'
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
                    name="Run",
                    tooltip="Run Workflow",
                    image=ImageResource("baseline_play_arrow_black_48dp"),
                    method="setup_task.run_bdss",
                    enabled_name="run_enabled",
                    image_size=(64, 64)
                ),
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
                    name="Open Project",
                    tooltip="Open a project containing a workflow and results",
                    image=ImageResource("baseline_folder_open_black_48dp"),
                    method="open_project",
                    image_size=(64, 64)
                ),
                TaskAction(
                    name="Save Project As",
                    tooltip="Save results and workflow together as JSON",
                    image=ImageResource("outline_save_black_48dp"),
                    method="save_project_as",
                    enabled_name="export_results_enabled",
                    image_size=(64, 64)
                ),
                TaskAction(
                    name="Export Results",
                    tooltip="Export results table to a JSON or CSV file",
                    image=ImageResource("baseline_save_black_48dp"),
                    method="export_analysis_model_as",
                    enabled_name="export_results_enabled",
                    image_size=(64, 64)
                ),
                TaskAction(
                    name="Plugins",
                    tooltip="View state of loaded plugins",
                    image=ImageResource("baseline_power_black_48dp"),
                    method="setup_task.open_plugins",
                    image_size=(64, 64)
                ),
            ),
        ]

    def create_central_pane(self):
        """ Creates the central pane which contains the analysis part
        (pareto front and output KPI values)
        """
        central_pane = DataViewPane(analysis_model=self.analysis_model)
        self.central_pane = central_pane
        return central_pane

    def create_dock_panes(self):
        """ Creates the dock panes """
        return [self.side_pane]

    # Default initialisers

    def _side_pane_default(self):
        return ResultsPane(analysis_model=self.analysis_model)

    def _default_layout_default(self):
        """ Defines the default layout of the task window """
        return TaskLayout(
            top=PaneItem('force_wfmanager.results_pane'),
        )

    def _workflow_model_default(self):
        return None

    def _analysis_model_default(self):
        return AnalysisModel()

    # Save AnalysisModel to file and sync its state

    @on_trait_change('analysis_model.export_enabled')
    def sync_export_enabled(self):
        self.export_results_enabled = self.analysis_model.export_enabled

    def export_analysis_model_as(self):
        """ Shows a dialog to save the :class:`AnalysisModel` as a
        JSON file.

        """
        dialog = FileDialog(
            action="save as",
            default_filename="results.json",
            wildcard='JSON files (*.json)|*.json|CSV files (*.csv)|*.csv',
        )

        result = dialog.open()

        if result is not OK:
            return False

        current_file = dialog.path

        if self._write_analysis(current_file):
            return True

        return False

    def _write_analysis(self, file_path):
        """ Write the contents of the analysis model to a JSON file.

        Parameters
        ----------
        file_path (str)
            the name of the file to write to.

        Returns
        -------
        bool: true if save was successful.

        """
        try:
            write_analysis_model(self.analysis_model, file_path)
        except IOError as e:
            error(
                None,
                'Cannot save in the requested file:\n\n{}'.format(
                    str(e)),
                'Error when saving the results table'
            )
            log.exception('Error when saving AnalysisModel')
            return False
        except Exception as e:
            error(
                None,
                'Cannot save the results table:\n\n{}'.format(
                    str(e)),
                'Error when saving results'
            )
            log.exception('Error when saving results')
            return False
        else:
            self.current_file = file_path
            return True

    def save_project_as(self):
        """ Shows a dialog to save the current project as a JSON file. """
        dialog = FileDialog(
            action="save as",
            default_filename="project.json",
            wildcard='JSON files (*.json)|*.json',
        )

        result = dialog.open()

        if result is not OK:
            return False

        current_file = dialog.path

        if self._write_project(current_file):
            self.current_file = current_file
            return True

        return False

    def _write_project(self, file_path):
        """ Writes a JSON file that contains the :attr:`Workflow` and
        :attr:`AnalysisModel`.

        """
        try:
            write_project_file(self.workflow_model,
                               self.analysis_model, file_path)

        except IOError as e:
            error(
                None,
                'Cannot save in the requested file:\n\n{}'.format(
                    str(e)),
                'Error when saving the project'
            )
            log.exception('Error when saving Project')
            return False

        except Exception as e:
            error(
                None,
                'Cannot save the Project:\n\n{}'.format(
                    str(e)),
                'Error when saving results'
            )
            log.exception('Error when the Project')
            return False
        else:
            return True

    def open_project(self):
        """ Shows a dialog to open a JSON file and load the contents into
        :attr:`Workflow` and :attr:`AnalysisModel`.

        """

        dialog = FileDialog(
            action="open",
            wildcard='JSON files (*.json)|*.json',
        )

        result = dialog.open()

        if result is not OK:
            return False

        current_file = dialog.path

        if self._load_project(current_file):
            return True

        return False

    def _load_project(self, file_path):
        """ Load contents of JSON file into:attr:`Workflow` and
        :attr:`AnalysisModel`.

        """
        try:
            (analysis_model_dict,
             self.workflow_model) = load_project_file(
                self.factory_registry, file_path)

            # create two separate workflows, so that setup task can be
            # edited without changing the review task copy
            self.setup_task.workflow_file.workflow_model = (
                copy.copy(self.workflow_model))

            # share the analysis model with the setup_task
            self.analysis_model.from_dict(analysis_model_dict)
            self.setup_task.analysis_model = self.analysis_model

        except KeyError as e:
            error(
                None,
                'Unable to find analysis model:\n\n{}'.format(
                    str(e)),
                'Error when loading project'
            )
            log.exception('KeyError when loading project')
            return False

        except IOError as e:
            error(
                None,
                'Unable to load file:\n\n{}'.format(
                    str(e)),
                'Error when loading project'
            )
            log.exception('Error loading project file')
            return False

        except Exception as e:
            error(
                None,
                'Unable to load project:\n\n{}'.format(
                    str(e)),
                'Error when loading project'
            )
            log.exception('Error when loading project')
            return False

        else:
            self.current_file = file_path
            return True

    # Synchronization with Setup Task

    @on_trait_change('setup_task.run_enabled')
    def sync_run_enabled(self):
        self.run_enabled = self.setup_task.run_enabled

    @on_trait_change('setup_task.save_load_enabled')
    def sync_save_load_enabled(self):
        self.save_load_enabled = self.setup_task.save_load_enabled

    # Synchronization with Window

    @on_trait_change('window.tasks')
    def sync_setup_task(self):
        if self.window is not None:
            for task in self.window.tasks:
                if task.name == "Workflow Setup":
                    self.setup_task = task
                    self.analysis_model = self.setup_task.analysis_model

    @on_trait_change('setup_task.computation_running')
    def cache_running_workflow(self):
        """ When a new computation starts running, save a copy of the
        :attr:`setup_task.workflow_model` as :attr:workflow_model` that
        can be used when saving the results of the run alongside the
        workflow that created it.
        """
        if self.setup_task.computation_running:
            with tempfile.TemporaryFile(mode='w+t') as fp:
                WorkflowWriter().write(self.setup_task.workflow_model, fp)
                reader = WorkflowReader(self.setup_task.factory_registry)
                fp.seek(0)
                self.workflow_model = reader.read(fp)

    # Menu/Toolbar Methods

    def switch_task(self):
        if self.setup_task is not None:
            self.window.activate_task(self.setup_task)

    def exit(self):
        self.window.close()
