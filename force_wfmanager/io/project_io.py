import logging
import json

from force_bdss.api import WorkflowWriter, WorkflowReader

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
    with open(file_path, "w") as output:
        # create a dictionary that contains analysis model,
        # workflow and version that can be read back in by
        # :class:`WorkflowReader`, and dump to JSON
        project_json = {}
        writer = WorkflowWriter()
        project_json["analysis_model"] = analysis_model.as_json()
        project_json["workflow"] = writer.get_workflow_data(workflow_model)
        project_json["version"] = writer.version
        json.dump(project_json, output, indent=4)


def load_project_file(factory_registry, file_path):
    """ Passes the `file_path` to the WorkflowReader and
    the analysis model loader, to create a Workflow object and
    an analysis model dictionary.

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
    workflow_model: Workflow
        Workflow instance
    """
    analysis_model_dict = load_analysis_model(file_path)

    reader = WorkflowReader(factory_registry)
    workflow_model = reader.read(file_path)

    return analysis_model_dict, workflow_model


def load_analysis_model(file_path):
    """ Opens the `file_path` file and loads the json. Returns the
    'analysis_model' value from the JSON, or an empty dictionary.
    """
    with open(file_path, "r") as fp:
        project_json = json.load(fp)

    analysis_model_dict = project_json.get("analysis_model", {})
    return analysis_model_dict
