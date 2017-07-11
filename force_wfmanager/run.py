from pyface.api import GUI
from pyface.tasks.api import TaskWindow

# Local imports.
from wfmanager import WfManager


def main():
    gui = GUI()

    task = WfManager()
    window = TaskWindow(size=(800, 600))
    window.add_task(task)
    window.open()

    gui.start_event_loop()
