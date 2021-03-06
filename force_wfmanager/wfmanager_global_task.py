#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

import logging

from pyface.api import ImageResource
from pyface.tasks.action.api import (
    SMenu, SToolBar, TaskAction, SchemaAddition)
from envisage.ui.tasks.task_extension import TaskExtension
from traits.api import List, Callable

from force_wfmanager.wfmanager import TaskToggleGroupAccelerator


log = logging.getLogger(__name__)


class WfManagerGlobalTask(TaskExtension):
    """Global extensions to Setup and Review tasks.
    """

    # The ID of the task to extend. If the ID is omitted, the extension applies
    # to all tasks.
    # NO TASK_ID as this is a global task extension

    # A list of menu bar and tool bar items to add to the set provided
    # by the task.
    actions = List(SchemaAddition)

    # A list of dock pane factories that will extend the dock panes provided by
    # the task.
    dock_pane_factories = List(Callable)

    def _actions_default(self):
        """ Traits default.
        :return: list of schema's to be added to all tasks ("globally").
        """

        return [
                SchemaAddition(
                    path='mymenu',
                    factory=self.file_menu,
                    id='file.menu.schema',
                ),
                SchemaAddition(
                    path='mymenu',
                    factory=self.view_menu,
                    id='file.view.schema',
                ),
                SchemaAddition(
                    path='mymenu',
                    factory=self.help_menu,
                    id='file.help.schema',
                ),
                SchemaAddition(
                    path='',
                    factory=self.run_tools,
                    id='tools.run.schema',
                ),
            ]

    def file_menu(self):
        """ File menu schema.
        """
        return SMenu(
                TaskAction(
                    name="Open Workflow...",
                    method="setup_task.open_workflow",
                    enabled_name="setup_task.save_load_enabled",
                    accelerator="Ctrl+O",
                ),
                TaskAction(
                    id="Save",
                    name="Save Workflow",
                    method="setup_task.save_workflow",
                    enabled_name="setup_task.save_load_enabled",
                    accelerator="Ctrl+S",
                ),
                TaskAction(
                    name="Save Workflow as...",
                    method="setup_task.save_workflow_as",
                    enabled_name="setup_task.save_load_enabled",
                    accelerator="Shift+Ctrl+S",
                ),
                TaskAction(name="Plugins...",
                           method="setup_task.open_plugins"),
                name="&File",
            )

    def view_menu(self):
        """ View menu schema.
        """
        return SMenu(TaskToggleGroupAccelerator(), id="View", name="&View")

    def help_menu(self):
        """ Help menu schema.
        """
        return SMenu(
                TaskAction(
                    name="About WorkflowManager...",
                    method="setup_task.open_about"
                ),
                TaskAction(
                    name="Online Documentation",
                    method="setup_task.open_documentation"
                ),
                TaskAction(
                    name="BDSS Tutorial",
                    method="setup_task.open_tutorial"
                ),
                name="&Help",
                id='Help'
            )

    def run_tools(self):
        """ Run/pause/stop workflow tools schema.
        """
        return SToolBar(
                TaskAction(
                    name="Run",
                    tooltip="Run Workflow",
                    image=ImageResource("baseline_play_arrow_black_48dp"),
                    method="setup_task.run_bdss",
                    enabled_name="setup_task.run_enabled",
                    image_size=(64, 64),
                ),
                TaskAction(
                    name="Stop",
                    tooltip="Stop Workflow",
                    method="setup_task.stop_bdss",
                    enabled_name='setup_task.computation_running',
                    image=ImageResource("baseline_stop_black_18dp"),
                    image_size=(64, 64),
                ),
                TaskAction(
                    name="Pause",
                    tooltip="Pause Workflow",
                    method="setup_task.pause_bdss",
                    enabled_name='setup_task.computation_running',
                    visible_name='setup_task._not_paused',
                    image=ImageResource("baseline_pause_black_18dp"),
                    image_size=(64, 64),
                ),
                TaskAction(
                    name="Resume",
                    tooltip="Resume Workflow",
                    method="setup_task.pause_bdss",
                    enabled_name='setup_task.computation_running',
                    visible_name='setup_task._paused',
                    image=ImageResource("baseline_skip_next_black_18dp"),
                    image_size=(64, 64),
                ),
        )
