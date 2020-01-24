import copy
from unittest import mock, TestCase

from pyface.api import OK, CANCEL
from pyface.file_dialog import FileDialog
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from pyface.tasks.api import TaskWindow

from force_bdss.tests.probe_classes.factory_registry import (
    ProbeFactoryRegistry,
)
from force_bdss.api import Workflow
from force_wfmanager.tests.dummy_classes.dummy_contributed_ui import (
    DummyContributedUI,
)
from force_wfmanager.ui.review.data_view_pane import DataViewPane
from force_wfmanager.ui.setup.setup_pane import SetupPane
from force_wfmanager.ui.setup.side_pane import SidePane
from force_wfmanager.ui.review.results_pane import ResultsPane
from force_wfmanager.model.analysis_model import AnalysisModel

from .mock_methods import (
    mock_file_reader,
    mock_file_writer,
    mock_dialog,
    mock_return_args,
)
from force_wfmanager.tests.dummy_classes.dummy_wfmanager import DummyWfManager

from force_wfmanager.wfmanager_review_task import WfManagerReviewTask
from force_wfmanager.wfmanager_setup_task import WfManagerSetupTask

FILE_DIALOG_PATH = "force_wfmanager.wfmanager_setup_task.FileDialog"
RESULTS_FILE_DIALOG_PATH = "force_wfmanager.wfmanager_review_task.FileDialog"
RESULTS_FILE_OPEN_PATH = "force_wfmanager.io.project_io.open"
RESULTS_JSON_DUMP_PATH = "force_wfmanager.io.project_io.json.dump"
RESULTS_JSON_LOAD_PATH = "force_wfmanager.io.project_io.json.load"
RESULTS_WRITER_PATH = (
    "force_wfmanager.io.project_io.WorkflowWriter.get_workflow_data"
)
RESULTS_READER_PATH = "force_wfmanager.io.project_io.WorkflowReader"
RESULTS_ERROR_PATH = "force_wfmanager.wfmanager_review_task.error"
ANALYSIS_WRITE_PATH = (
    "force_wfmanager.io.analysis_model_io." "write_analysis_model"
)
ANALYSIS_FILE_OPEN_PATH = "force_wfmanager.io.analysis_model_io.open"


def get_probe_wfmanager_tasks(wf_manager=None, contributed_uis=None):
    # Returns the Setup and Review Tasks, with a mock TaskWindow and dummy
    # Application which does not have an event loop.

    if wf_manager is None:
        wf_manager = DummyWfManager()

    analysis_model = AnalysisModel()
    workflow_model = Workflow()
    factory_registry_plugin = ProbeFactoryRegistry()
    if contributed_uis is None:
        contributed_uis = [DummyContributedUI()]

    wf_manager.factory_registry = factory_registry_plugin

    setup_test = WfManagerSetupTask(
        analysis_model=analysis_model,
        workflow_model=workflow_model,
        factory_registry=factory_registry_plugin,
        contributed_uis=contributed_uis,
    )

    review_task = WfManagerReviewTask(
        analysis_model=analysis_model,
        workflow_model=workflow_model,
        factory_registry=factory_registry_plugin,
    )

    tasks = [setup_test, review_task]
    mock_window = mock.Mock(spec=TaskWindow)
    mock_window.tasks = tasks
    mock_window.application = wf_manager

    for task in tasks:
        task.window = mock_window
        task.create_central_pane()

        # A Task's central pane is generally aware of its task in normal
        # operations, but it doesn't seem to be so in this mock situation;
        # so we "make" it aware.
        if hasattr(task, "central_pane") and task.central_pane is not None:
            task.central_pane.task = task

        task.create_dock_panes()

    return tasks[0], tasks[1]


class TestWFManagerTasks(GuiTestAssistant, TestCase):
    def setUp(self):
        super(TestWFManagerTasks, self).setUp()
        self.setup_task, self.review_task = get_probe_wfmanager_tasks()

    def test_init(self):
        self.assertIsInstance(self.setup_task.create_central_pane(), SetupPane)
        self.assertEqual(len(self.setup_task.create_dock_panes()), 1)
        self.assertIsInstance(self.setup_task.side_pane, SidePane)

        self.assertEqual(len(self.review_task.create_dock_panes()), 1)
        self.assertIsInstance(self.review_task.side_pane, ResultsPane)
        self.assertIsInstance(
            self.review_task.create_central_pane(), DataViewPane
        )
        self.assertIsInstance(self.review_task.workflow_model, Workflow)
        self.assertIsInstance(self.setup_task.workflow_model, Workflow)
        self.assertIsInstance(self.review_task.analysis_model, AnalysisModel)
        self.assertIsInstance(self.setup_task.analysis_model, AnalysisModel)

    def test_save_analysis(self):
        mock_open = mock.mock_open()
        with mock.patch(
            RESULTS_FILE_DIALOG_PATH
        ) as mock_file_dialog, mock.patch(
            ANALYSIS_FILE_OPEN_PATH, mock_open, create=False
        ):

            mock_file_dialog.side_effect = mock_dialog(
                FileDialog, OK, "test_file.json"
            )

            self.assertTrue(self.review_task.export_analysis_model_as())
            self.assertTrue(mock_file_dialog.called)
            self.assertTrue(mock_open.called)

        mock_open = mock.mock_open()
        with mock.patch(
            RESULTS_FILE_DIALOG_PATH
        ) as mock_file_dialog, mock.patch(
            ANALYSIS_FILE_OPEN_PATH, mock_open, create=False
        ):
            mock_file_dialog.side_effect = mock_dialog(
                FileDialog, OK, "test_file.csv"
            )

            self.assertTrue(self.review_task.export_analysis_model_as())
            self.assertTrue(mock_file_dialog.called)
            self.assertTrue(mock_open.called)

    def test_save_analysis_failure(self):
        mock_open = mock.mock_open()
        with mock.patch(
            RESULTS_FILE_DIALOG_PATH
        ) as mock_file_dialog, mock.patch(
            ANALYSIS_FILE_OPEN_PATH, mock_open, create=False
        ):

            mock_file_dialog.side_effect = mock_dialog(FileDialog, CANCEL)

            self.assertFalse(self.review_task.export_analysis_model_as())
            self.assertTrue(mock_file_dialog.called)
            self.assertFalse(mock_open.called)

        mock_open = mock.mock_open()
        mock_open.side_effect = IOError("OUPS")
        with mock.patch(
            RESULTS_FILE_DIALOG_PATH
        ) as mock_file_dialog, mock.patch(
            ANALYSIS_FILE_OPEN_PATH, mock_open, create=False
        ), mock.patch(
            RESULTS_ERROR_PATH
        ) as mock_error:
            mock_error.side_effect = mock_return_args
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK, "")

            self.assertFalse(self.review_task.export_analysis_model_as())
            self.assertTrue(mock_file_dialog.called)
            self.assertTrue(mock_open.called)

            mock_error.assert_called_with(
                None,
                "Cannot save in the requested file:\n\nOUPS",
                "Error when saving the results table",
            )

        mock_open = mock.mock_open()
        mock_open.side_effect = RuntimeError("OUPS")
        with mock.patch(
            RESULTS_FILE_DIALOG_PATH
        ) as mock_file_dialog, mock.patch(
            ANALYSIS_FILE_OPEN_PATH, mock_open, create=False
        ), mock.patch(
            RESULTS_ERROR_PATH
        ) as mock_error:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK, "")

            self.assertFalse(self.review_task.export_analysis_model_as())
            self.assertTrue(mock_file_dialog.called)
            self.assertTrue(mock_open.called)

            mock_error.assert_called_with(
                None,
                "Cannot save the results table:\n\nOUPS",
                "Error when saving results",
            )

    def test_save_project(self):
        mock_open = mock.mock_open()
        with mock.patch(
            RESULTS_FILE_DIALOG_PATH
        ) as mock_file_dialog, mock.patch(
            RESULTS_JSON_DUMP_PATH
        ) as mock_json_dump, mock.patch(
            RESULTS_FILE_OPEN_PATH, mock_open, create=True
        ), mock.patch(
            RESULTS_WRITER_PATH
        ) as mock_wf_writer:
            mock_file_dialog.side_effect = mock_dialog(
                FileDialog, OK, "file_path"
            )
            mock_wf_writer.side_effect = mock_file_writer

            self.review_task.save_project_as()

            self.assertTrue(mock_wf_writer.called)
            self.assertTrue(mock_open.called)
            self.assertTrue(mock_json_dump.called)
            self.assertTrue(mock_file_dialog.called)

    def test_save_project_failure(self):
        mock_open = mock.mock_open()
        mock_open.side_effect = IOError("OUPS")
        with mock.patch(
            RESULTS_FILE_DIALOG_PATH
        ) as mock_file_dialog, mock.patch(
            RESULTS_FILE_OPEN_PATH, mock_open, create=True
        ), mock.patch(
            RESULTS_ERROR_PATH
        ) as mock_error:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_error.side_effect = mock_return_args

            self.review_task.save_project_as()

            self.assertTrue(mock_open.called)
            mock_error.assert_called_with(
                None,
                "Cannot save in the requested file:\n\nOUPS",
                "Error when saving the project",
            )

    def test_open_project(self):
        mock_open = mock.mock_open()
        with mock.patch(
            RESULTS_FILE_DIALOG_PATH
        ) as mock_file_dialog, mock.patch(
            RESULTS_JSON_LOAD_PATH
        ) as mock_json, mock.patch(
            RESULTS_FILE_OPEN_PATH, mock_open, create=True
        ):

            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_json.return_value = {
                "analysis_model": {"x": [1], "y": [2]},
                "version": "1",
                "workflow": {},
            }

            # the workflow gets updated to a new Workflow object
            old_workflow = self.review_task.workflow_model
            # but the analysis model gets updated in-place
            old_analysis = copy.deepcopy(self.review_task.analysis_model)
            self.assertEqual(old_workflow, self.setup_task.workflow_model)

            self.review_task.open_project()

            self.assertTrue(mock_open.called)
            self.assertTrue(mock_json.called)

            self.assertNotEqual(old_workflow, self.review_task.workflow_model)
            self.assertNotEqual(
                self.setup_task.workflow_model, self.review_task.workflow_model
            )

            self.assertNotEqual(old_workflow, self.setup_task.workflow_model)
            self.assertNotEqual(
                old_workflow, self.setup_task.side_pane.workflow_tree.model
            )
            self.assertNotEqual(
                old_analysis.value_names,
                self.review_task.analysis_model.value_names,
            )
            self.assertNotEqual(
                old_analysis.value_names,
                self.setup_task.analysis_model.value_names,
            )
            self.assertEqual(
                self.review_task.analysis_model.value_names, ("x", "y")
            )
            self.assertEqual(
                self.review_task.analysis_model.evaluation_steps, [(1, 2)]
            )
            self.assertEqual(
                self.setup_task.analysis_model.value_names,
                self.review_task.analysis_model.value_names,
            )
            self.assertEqual(
                self.setup_task.analysis_model.evaluation_steps,
                self.review_task.analysis_model.evaluation_steps,
            )

    def test_open_project_failure(self):
        mock_open = mock.mock_open()
        mock_open.side_effect = IOError("OUPS")
        with mock.patch(
            RESULTS_FILE_DIALOG_PATH
        ) as mock_file_dialog, mock.patch(RESULTS_ERROR_PATH) as mock_error:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)

            self.assertFalse(self.review_task.open_project())
            error_msg = (
                "Unable to load file:\n\n[Errno 2] "
                "No such file or directory: ''"
            )
            mock_error.assert_called_with(
                None, error_msg, "Error when loading project"
            )

        mock_open = mock.mock_open()
        with mock.patch(
            RESULTS_FILE_DIALOG_PATH
        ) as mock_file_dialog, mock.patch(
            RESULTS_JSON_LOAD_PATH
        ) as mock_json, mock.patch(
            RESULTS_ERROR_PATH
        ) as mock_error, mock.patch(
            RESULTS_FILE_OPEN_PATH, mock_open, create=True
        ), mock.patch(
            RESULTS_READER_PATH
        ) as mock_reader:
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)
            mock_reader.side_effect = mock_file_reader
            mock_json.return_value = {
                "asdfsadf": {"x": [1], "y": [2]},
                "123456": "1",
                "blah": {},
            }

            success = self.review_task.open_project()
            old_workflow = self.review_task.workflow_model
            old_analysis = self.review_task.analysis_model
            self.assertTrue(mock_open.called)
            self.assertTrue(mock_json.called)
            self.assertFalse(success)
            # it should not get to the stage where the wfreader is called
            self.assertFalse(mock_reader.called)
            mock_error.assert_called_with(
                None,
                "Unable to find analysis model:\n\n{}".format(
                    "'analysis_model'"
                ),
                "Error when loading project",
            )
            self.assertEqual(old_workflow, self.setup_task.workflow_model)
            self.assertEqual(old_analysis, self.setup_task.analysis_model)
            self.assertEqual(old_workflow, self.review_task.workflow_model)
            self.assertEqual(old_analysis, self.review_task.analysis_model)

        mock_open = mock.mock_open()
        error = ValueError("some wrong value")
        mock_open.side_effect = error
        with mock.patch(
            RESULTS_FILE_DIALOG_PATH
        ) as mock_file_dialog, mock.patch(
            RESULTS_ERROR_PATH
        ) as mock_error, mock.patch(
            RESULTS_FILE_OPEN_PATH, mock_open, create=True
        ):
            mock_file_dialog.side_effect = mock_dialog(FileDialog, OK)

            self.assertFalse(self.review_task.open_project())
            error_msg = f"Unable to load project:\n\n{error}"
            mock_error.assert_called_with(
                None, error_msg, "Error when loading project"
            )
