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
    id = 'pyface.tasks.contrib.python_shell.pane'
    name = 'Python Shell'

    editor = Instance(PythonShell)

    bindings = List(Dict)
    commands = List(Str)

    #: Remove the possibility to close the pane
    closable = False

    #: Remove the possibility to detach the pane from the GUI
    floatable = False

    #: Remove the possibility to move the pane in the GUI
    movable = False

    #: Make the pane visible by default
    visible = True

    def create_contents(self, parent):
        """ Create the python shell task pane

        This wraps the standard pyface PythonShell
        """
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

