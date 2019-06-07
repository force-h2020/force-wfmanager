import logging
import json

from force_bdss.api import (
    WorkflowReader, WorkflowWriter)
from pyface.api import error

log = logging.getLogger(__name__)


def write_project_file(workflow, file_path):
    """ Writes a JSON file that contains the :attr:`Workflow` and
    :attr:`AnalysisModel`.

    """
    try:
        with open(file_path, 'w') as output:
            # create a dictionary that contains analysis model,
            # workflow and version that can be read back in by
            # :class:`WorkflowReader`, and dump to JSON
            project_json = {}
            project_json['analysis_model'] = workflow.analysis_model.as_json()
            project_json['workflow'] = WorkflowWriter() \
                .get_workflow_data(workflow.workflow_model)
            project_json['version'] = WorkflowWriter().version
            json.dump(project_json, output, indent=4)

    except IOError as e:
        error(
            None,
            'Cannot save in the requested file:\n\n{}'.format(
                str(e)),
            'Error when saving the project'
        )
        log.exception('Error when saving Project')
        return False

    except Exception as e:
        error(
            None,
            'Cannot save the Project:\n\n{}'.format(
                str(e)),
            'Error when saving results'
        )
        log.exception('Error when the Project')
        return False
    else:
        return True


def load_project_file(workflow, file_path):
    """ Load contents of JSON file into:attr:`Workflow` and
    :attr:`AnalysisModel`.

    """

    try:
        with open(file_path, 'r') as fp:
            project_json = json.load(fp)

            # share the analysis model with the setup_task
            workflow.analysis_model.from_dict(project_json['analysis_model'])
            workflow.setup_task.analysis_model = workflow.analysis_model

            # create two separate workflows, so that setup task can be
            # edited without changing the results task copy
            reader = WorkflowReader(workflow.setup_task.factory_registry)
            fp.seek(0)
            workflow.workflow_model = reader.read(fp)
            fp.seek(0)
            workflow.setup_task.workflow_model = reader.read(fp)

    except KeyError as e:
        error(
            None,
            'Unable to find analysis model:\n\n{}'.format(
                str(e)),
            'Error when loading project'
        )
        log.exception('KeyError when loading project')
        return False

    except IOError as e:
        error(
            None,
            'Unable to load file:\n\n{}'.format(
                str(e)),
            'Error when loading project'
        )
        log.exception('Error loading project file')
        return False

    except Exception as e:
        error(
            None,
            'Unable to load project:\n\n{}'.format(
                str(e)),
            'Error when loading project'
        )
        log.exception('Error when loading project')
        return False

    else:
        return True
