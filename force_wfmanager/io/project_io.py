import logging
import json

from force_bdss.api import Workflow, WorkflowWriter, WorkflowReader

log = logging.getLogger(__name__)


def write_project_file(workflow_model, analysis_model, file_path):
    """ Writes a JSON file that contains the :attr:`Workflow` and
    :attr:`AnalysisModel`.

    Parameters
    ----------
    workflow_model:
        Workflow model
    analysis_model:
        Analysis model. Contains the results that are displayed in the plot
        and table
    file_path: str
        The file_path pointing to the file in which you want to read the
        project file
    """
    with open(file_path, 'w') as output:
        # create a dictionary that contains analysis model,
        # workflow and version that can be read back in by
        # :class:`WorkflowReader`, and dump to JSON
        project_json = {}
        writer = WorkflowWriter()
        project_json['analysis_model'] = analysis_model.as_json()
        project_json['workflow'] = writer.get_workflow_data(workflow_model)
        project_json['version'] = writer.version
        json.dump(project_json, output, indent=4)


def load_project_file(factory_registry, file_path):
    """ Load contents of JSON file into:attr:`Workflow` and
    :attr:`AnalysisModel`.

    Parameters
    ----------
    factory_registry:
        Workflow factory registry
    file_path: str
        The file_path pointing to the file in which you want to read the
        project file

    Returns
    -------
    analysis_model_dict: dict
        Dictionary of analysis model to read, needs to be parsed by
        the analysis model object of the workflow to be loaded in
    workflow_model:
        Workflow model
    """

    with open(file_path, 'r') as fp:
        project_json = json.load(fp)

    analysis_model_dict = project_json['analysis_model']

    reader = WorkflowReader(factory_registry)
    workflow_data = reader.parse_data(project_json)

    workflow_model = Workflow.from_json(factory_registry, workflow_data)

    return analysis_model_dict, workflow_model
