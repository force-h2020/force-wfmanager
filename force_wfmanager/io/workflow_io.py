import logging

from force_bdss.api import (
    InvalidFileException, WorkflowReader, WorkflowWriter)
from pyface.api import error

log = logging.getLogger(__name__)


def write_workflow_file(workflow, file_path):
    """ Creates a JSON file in the file_path and write the workflow
    description in it

    Parameters
    ----------
    file_path: str
        The file_path pointing to the file in which you want to write the
        workflow

    Returns
    -------
    Boolean:
        True if it was a success to write in the file, False otherwise
    """
    for hook_manager in workflow.ui_hooks_managers:
        try:
            hook_manager.before_save(workflow)
        except Exception:
            log.exception(
                "Failed before_save hook "
                "for hook manager {}".format(
                    hook_manager.__class__.__name__)
            )

    try:
        with open(file_path, 'w') as output:
            WorkflowWriter().write(workflow.workflow_model, output)
    except IOError as e:
        error(
            None,
            'Cannot save in the requested file:\n\n{}'.format(
                str(e)),
            'Error when saving workflow'
        )
        log.exception('Error when saving workflow')
        return False
    except Exception as e:
        error(
            None,
            'Cannot save the workflow:\n\n{}'.format(
                str(e)),
            'Error when saving workflow'
        )
        log.exception('Error when saving workflow')
        return False
    else:
        return True


def load_workflow_file(workflow, f_name):
    """ Opens a workflow from the specified file name

    Parameters
    ----------
    f_name: str
        The path to the workflow file
    """
    reader = WorkflowReader(workflow.factory_registry)
    try:
        with open(f_name, 'r') as fobj:
            workflow.workflow_model = reader.read(fobj)
    except InvalidFileException as e:
        error(
            None,
            'Cannot read the requested file:\n\n{}'.format(
                str(e)),
            'Error when reading file'
        )
    else:
        workflow.current_file = f_name