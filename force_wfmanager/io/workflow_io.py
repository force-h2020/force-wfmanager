import logging

from force_bdss.api import WorkflowWriter, WorkflowReader

log = logging.getLogger(__name__)


def write_workflow_file(workflow_model, file_path):
    """ Creates a JSON file in the file_path and write the workflow
    description in it

    Parameters
    ----------
    workflow_model:
        Workflow model to be written to file
    file_path: str
        The file_path pointing to the file in which you want to write the
        workflow
    """
    WorkflowWriter().write(workflow_model, file_path)


def load_workflow_file(factory_registry, file_path):
    """ Loads a JSON from file path and reads the workflow
     description in it

    Parameters
    ----------
    factory_registry:
        Workflow factory registry
    file_path: str
        The file_path pointing to the file in which you want to read the
        workflow
    """

    reader = WorkflowReader(factory_registry)

    workflow_model = reader.read(file_path)

    return workflow_model
