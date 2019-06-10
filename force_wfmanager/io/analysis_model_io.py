import logging


log = logging.getLogger(__name__)


def write_analysis_model(analysis_model, file_path):
    """ Write the contents of the analysis model to a JSON or CSV file.

    Parameters
    ----------
    file_path (str)
        the name of the file to write to.
    """
    with open(file_path, 'w') as output:
        if file_path.endswith('.json'):
            analysis_model.write_to_json(output)
        elif file_path.endswith('.csv'):
            analysis_model.write_to_csv(output)
        else:
            raise IOError('Unrecognised file type, should be one of '
                          'JSON/CSV.')
