import logging
import os
import subprocess
import tempfile

from envisage.ui.tasks.tasks_application import TasksApplication

from pyface.api import error, YES, GUI, confirm
from pyface.tasks.action.api import SMenuBar
from pyface.tasks.api import Task, TaskLayout, PaneItem

from traits.api import Instance, on_trait_change

from force_bdss.api import WorkflowWriter

from force_wfmanager.central_pane.setup_pane import SetupPane
from force_wfmanager.left_side_pane.tree_pane import TreePane

log = logging.getLogger(__name__)


class WfManagerSetupTask(Task):
    id = 'force_wfmanager.wfmanager_setup_task'
    name = 'Workflow Manager'

    #: Side Pane containing the tree editor for the Workflow and the Run button
    side_pane = Instance(TreePane)

    #: The application associated with this Task
    app = Instance(TasksApplication)

    #: The menu bar for this task.
    menu_bar = Instance(SMenuBar)

    def __init__(self, shared_menu_bar):
        self.menu_bar = shared_menu_bar
        super(WfManagerSetupTask, self).__init__()

    # TODO: Add a nice looking toolbar

    def create_central_pane(self):
        """ Creates the central pane which contains the analysis part
        (pareto front and output KPI values)
        """
        return SetupPane(self.app.analysis_m)

    def create_dock_panes(self):
        """ Creates the dock panes """
        return [self.side_pane]

    @on_trait_change('app.computation_running')
    def update_side_pane_status(self):
        self.side_pane.ui_enabled = not self.app.computation_running
        self.app.save_load_enabled = not self.app.computation_running

    @on_trait_change('side_pane.run_button')
    def run_bdss(self):
        """ Run the BDSS computation """
        if len(self.app.analysis_m.evaluation_steps) != 0:
            result = confirm(
                None,
                "Are you sure you want to run the computation and "
                "empty the result table?")
            if result is not YES:
                return

        self.app.computation_running = True
        try:
            for hook_manager in self.app.ui_hooks_managers:
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
                WorkflowWriter().write(self.app.workflow_m, output)

            # Clear the analysis model before attempting to run
            self.app.analysis_m.clear()

            future = self.app.executor.submit(self._execute_bdss, tmpfile_path)
            future.add_done_callback(self._execution_done_callback)
        except Exception as e:
            logging.exception("Unable to run BDSS.")
            error(None,
                  "Unable to run BDSS: {}".format(e),
                  'Error when running BDSS'
                  )
            self.app.computation_running = False

    def _execute_bdss(self, workflow_path):
        """Secondary thread executor routine.
        This executes the BDSS and wait for its completion.
        """
        try:
            subprocess.check_call([self.app.bdss_executable_path,
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

        for hook_manager in self.app.ui_hooks_managers:
            try:
                hook_manager.after_execution(self)
            except Exception:
                log.exception(
                    "Failed after_execution hook "
                    "for hook manager {}".format(
                        hook_manager.__class__.__name__)
                )

        self.app.computation_running = False

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
            left=PaneItem('force_wfmanager.tree_pane'),
        )

    def _side_pane_default(self):
        return TreePane(
            factory_registry=self.app.factory_registry,
            workflow_m=self.app.workflow_m
        )

    def _app_default(self):
        return self.window.application

    # Handlers
    @on_trait_change('app.workflow_m')
    def update_side_pane(self):
        self.side_pane.workflow_m = self.app.workflow_m
