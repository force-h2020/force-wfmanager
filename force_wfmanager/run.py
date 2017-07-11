from pyface.api import GUI
from pyface.tasks.api import TaskWindow

# Local imports.
from example_task import ExampleTask


def main():
    gui = GUI()

    task = ExampleTask()
    window = TaskWindow(size=(800, 600))
    window.add_task(task)
    window.open()

    gui.start_event_loop()
