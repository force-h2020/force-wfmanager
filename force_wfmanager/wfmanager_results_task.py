import logging

from pyface.api import ImageResource, FileDialog, OK, error
from pyface.tasks.action.api import SMenuBar, SMenu, TaskAction, SToolBar
from pyface.tasks.api import Task, TaskLayout, PaneItem
from traits.api import Bool, Instance, List, on_trait_change

from force_bdss.api import Workflow
from force_wfmanager.central_pane.analysis_model import AnalysisModel
from force_wfmanager.central_pane.graph_pane import GraphPane
from force_wfmanager.left_side_pane.results_pane import ResultsPane
from force_wfmanager.task_toggle_group_accelerator import (
    TaskToggleGroupAccelerator
)

log = logging.getLogger(__name__)


class WfManagerResultsTask(Task):
    """Task responsible for running the Workflow and displaying the results."""

    #: Side Pane containing the tree editor for the Workflow and the Run button
    side_pane = Instance(ResultsPane)

    #: The menu bar for this task.
    menu_bar = Instance(SMenuBar)

    #: The tool bars for this task.
    tool_bars = List(SToolBar)

    id = 'force_wfmanager.wfmanager_results_task'
    name = 'Results'

    #: Workflow model.
    workflow_model = Instance(Workflow, allow_none=False)

    #: Analysis model. Contains the results that are displayed in the plot
    #: and table
    analysis_model = Instance(AnalysisModel, allow_none=False)

    #: Is the 'run' toolbar button active
    run_enabled = Bool(True)

    #: Are the saving and loading menu/toolbar buttons active
    save_load_enabled = Bool(True)

    #: Is the results saving button enabled?
    save_results_enabled = Bool(True)

    #: Setup Task
    setup_task = Instance(Task)

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
                    method='save_analysis_model_as',
                    enabled_name='save_results_enabled'
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
                    method="setup_task.open_workflow",
                    enabled_name="save_load_enabled",
                    image_size=(64, 64)
                ),
                TaskAction(
                    name="Save",
                    tooltip="Save workflow",
                    image=ImageResource("baseline_save_black_48dp"),
                    method="setup_task.save_workflow",
                    enabled_name="save_load_enabled",
                    image_size=(64, 64)
                ),
                TaskAction(
                    name="Save As",
                    tooltip="Save workflow with new filename",
                    image=ImageResource("outline_save_black_48dp"),
                    method="setup_task.save_workflow_as",
                    enabled_name="save_load_enabled",
                    image_size=(64, 64)
                ),
                TaskAction(
                    name="Save Results As",
                    tooltip="Save results table with new filename",
                    image=ImageResource("baseline_save_black_48dp"),
                    method="save_analysis_model_as",
                    enabled_name="save_results_enabled",
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
            SToolBar(
                TaskAction(
                    name="Run",
                    tooltip="Run Workflow",
                    image=ImageResource("baseline_play_arrow_black_48dp"),
                    method="setup_task.run_bdss",
                    enabled_name="run_enabled",
                    image_size=(64, 64)
                ),
            )
        ]

    def create_central_pane(self):
        """ Creates the central pane which contains the analysis part
        (pareto front and output KPI values)
        """
        return GraphPane(self.analysis_model)

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
        return Workflow()

    def _analysis_model_default(self):
        return AnalysisModel()

    # Save AnalysisModel to JSON file
    def save_analysis_model_as(self):
        """ Shows a dialog to save the analysis model into a JSON file """
        dialog = FileDialog(
            action="save as",
            default_filename="results.json",
            wildcard='JSON files (*.json)|*.json|CSV files (*.csv)|*.csv',
        )

        result = dialog.open()

        if result is not OK:
            return

        current_file = dialog.path

        if self._write_analysis_model(current_file):
            self.current_file = current_file
            return True
        return False

    def _write_analysis_model(self, file_path):
        """ Write the contents of the analysis model to a JSON file. """
        try:
            with open(file_path, 'w') as output:
                if file_path.endswith('.json'):
                    self.analysis_model.write_to_json(output)
                elif file_path.endswith('.csv'):
                    self.analysis_model.write_to_csv(output)
                else:
                    raise IOError('Unrecognised file type, should be one of '
                                  'JSON/CSV.')

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
    def get_setup_task(self):
        if self.window is not None:
            for task in self.window.tasks:
                if task.name == "Workflow Setup":
                    self.setup_task = task
                    self.analysis_model = self.setup_task.analysis_model
                    self.workflow_model = self.setup_task.workflow_model

    # Menu/Toolbar Methods

    def switch_task(self):
        if self.setup_task is not None:
            self.window.activate_task(self.setup_task)

    def exit(self):
        self.window.close()
