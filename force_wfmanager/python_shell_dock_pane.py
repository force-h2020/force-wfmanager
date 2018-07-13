# Std lib imports
import logging

# Enthought library imports.
from traits.api import Str, List, Dict, Instance
from pyface.api import PythonShell
from pyface.tasks.api import DockPane

# set up logging
logger = logging.getLogger()


class PythonShellDockPane(DockPane):
    """ A Tasks Pane containing a Pyface PythonShell
    """
    id = 'force_wfmanager.python_shell_dock_pane'
    name = 'Python Shell'

    editor = Instance(PythonShell)

    bindings = List(Dict)
    commands = List(Str)

    def create_contents(self, parent):
        """ Create the python shell task pane

        This wraps the standard pyface PythonShell
        """
        print("create contents")
        logger.debug('PythonShellPane: creating python shell pane')
        self.editor = PythonShell(parent)

        # bind namespace
        logger.debug('PythonShellPane: binding variables')
        for binding in self.bindings:
            for name, value in binding.items():
                self.editor.bind(name, value)

        # execute commands
        logger.debug('PythonShellPane: executing startup commands')
        for command in self.commands:
            self.editor.execute_command(command)

        logger.debug('PythonShellPane: created')
        return self.editor.control

