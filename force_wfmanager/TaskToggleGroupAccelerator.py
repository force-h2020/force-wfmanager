from pyface.action.api import ActionItem

from pyface.tasks.action.api import TaskToggleGroup
from pyface.tasks.action.task_toggle_group import TaskToggleAction


class TaskToggleGroupAccelerator(TaskToggleGroup):
    """The standard TaskToggleGroup from pyface, but with a keyboard shortcut
    for changing tasks (Ctrl + index of task)."""
    def _get_items(self):
        items = []
        for i, task in enumerate(self.window.tasks):
            action = TaskToggleAction(task=task,
                                      accelerator='Ctrl+{}'.format(i+1))
            items.append(ActionItem(action=action))
        return items
