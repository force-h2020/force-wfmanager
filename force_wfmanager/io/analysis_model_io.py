import logging

from pyface.api import error

log = logging.getLogger(__name__)


def write_analysis_model(workflow, file_path):
    """ Write the contents of the analysis model to a JSON file.

    Parameters
    ----------
    file_path (str)
        the name of the file to write to.

    Returns
    -------
    bool: true if save was successful.

    """
    try:
        with open(file_path, 'w') as output:
            if file_path.endswith('.json'):
                workflow.analysis_model.write_to_json(output)
            elif file_path.endswith('.csv'):
                workflow.analysis_model.write_to_csv(output)
            else:
                raise IOError('Unrecognised file type, should be one of '
                              'JSON/CSV.')

    except IOError as e:
        error(
            None,
            'Cannot save in the requested file:\n\n{}'.format(
                str(e)),
            'Error when saving the results table'
        )
        log.exception('Error when saving AnalysisModel')
        return False
    except Exception as e:
        error(
            None,
            'Cannot save the results table:\n\n{}'.format(
                str(e)),
            'Error when saving results'
        )
        log.exception('Error when saving results')
        return False
    else:
        return True
