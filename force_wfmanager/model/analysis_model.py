#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

import csv
import json
import logging

from traits.api import (
    Bool,
    Str,
    HasStrictTraits,
    List,
    Property,
    Tuple,
    TraitError,
    Dict,
    Either,
    Int,
    on_trait_change,
)

log = logging.getLogger(__name__)


class AnalysisModel(HasStrictTraits):

    #: Tuple of column names of the analysis model. The names are defined
    #: by the MCOStartEvent parsed in ``_server_event_mainthread()`` in
    #: :class:`WFManagerSetupTask
    #: <force_wfmanager.wfmanager_setup_task.WfManagerSetupTask>`.
    header = Tuple()

    #: The current row of the model. The received data is added to the
    #: `_row_data` first, before the whole row is added to the model table.
    _row_data = Dict(key_trait=Str)

    #: Storage for any metadata that is received along with the MCO data
    _row_metadata = Dict(key_trait=Str)

    #: Private trait of the `evaluation_steps` property
    _evaluation_steps = List(Tuple())

    #: Private trait of the `_step_metadata` property
    _step_metadata = List(Dict())

    #: Evaluation steps, each evaluation step is a tuple of parameter values,
    #: received from the a single Workflow execution. The order of
    #: the parameters in each evaluation step must match the order of
    #: value_names
    evaluation_steps = Property(List(Tuple()), depends_on="_evaluation_steps")

    #: Metadata associated with each evaluation step
    step_metadata = Property(List(Dict()), depends_on="_step_metadata")

    #: Tracks whether the current state of AnalysisModel can be exported
    _export_enabled = Bool(False)

    #: If there are results, then they can be exported
    export_enabled = Property(Bool(), depends_on="_export_enabled")

    #: Selected step, used for highlighting in the table/plot.
    #: If selected, it must be in the allowed range of values.
    _selected_step_indices = Either(None, List(Int()))

    #: Property that informs about the currently selected step.
    selected_step_indices = Property(
        Either(None, List(Int)), depends_on="_selected_step_indices"
    )

    #: Indicates whether there is any data stored in the AnalysisModel
    is_empty = Property(Bool(), depends_on="_evaluation_steps")

    def _header_default(self):
        return ()

    def _row_data_default(self):
        return dict.fromkeys(self.header)

    def _row_metadata_default(self):
        return {}

    def _get_export_enabled(self):
        return self._export_enabled

    def _get_step_metadata(self):
        return self._step_metadata

    def _get_evaluation_steps(self):
        return self._evaluation_steps

    def _get_selected_step_indices(self):
        return self._selected_step_indices

    def _set_selected_step_indices(self, values):
        """ Check the requested indices of selected rows, and use the
        requested values if they exist in the table, or are None.
        """
        if values is None:
            self._selected_step_indices = values
            return

        for value in values:
            if value > len(self.evaluation_steps) or value < 0:
                raise ValueError(
                    f"Invalid value for selection index {value}. "
                    "It must be a positive Int less or equal to "
                    f"{len(self.evaluation_steps)-1}"
                )

        self._selected_step_indices = values

    def _get_is_empty(self):
        return not bool(len(self.evaluation_steps))

    def notify(self, data, metadata=False):
        """ Public method to add `data` to the AnalysisModel.
        If no `header` is set up, the `data` is considered to be a
        `header`. If the metadata keyword is set to True the `data` is
        treated as metadata to be associated with the current row.
        Otherwise, the `data` is treated as to be added to the current row.
        """
        if not self.header:
            self._add_header(data)
        elif metadata:
            self._add_metadata(data)
        else:
            self._add_data(data)

    def _add_header(self, header):
        """ Creates the header of the AnalysisModel. Updates the
        current row to the default value with the header values as
        the keys."""
        try:
            self.header = header
        except TraitError as e:
            log.error(
                f"The Header of the AnalysisModel can't be defined by "
                f"the {header}. A list or tuple of strings is required."
            )
            raise e
        else:
            self._row_data = self._row_data_default()

    def _add_data(self, data):
        """ For a prepared AnalysisModel (when the header is already set up),
        adds `data` to the current row. The way the `data` is added depends
        on the format of the argument.
        If `data` is a dict-like object, `_add_cell` is called.
        Otherwise, `_add_cells` is called."""
        try:
            for key, value in data.items():
                self._add_cell(key, value)
        except AttributeError:
            self._add_cells(data)
            self._finalize_row()

    def _add_metadata(self, data):
        """ For each evaluation step, add optional metadata. Expects
        the `data` attribute to be a dictionary containing key value
        pairs to be associated with the current row.
        """
        try:
            self._row_metadata.update(data)
        except (TraitError, TypeError, ValueError):
            pass

    def _add_cell(self, label, value):
        """ Inserts a `value` into the column of the current row
        (self.row_data) with the `label` label."""
        if label in self.header:
            self._row_data.update({label: value})
        else:
            log.warning(
                f"The AnalysisModel does not have the {label} column."
                f"The value {value} has not been added to the table."
            )

    def _add_cells(self, data):
        """ Inserts the `data` to the `self.row_data`, starting from the
        first cell until every `data` element is inserted, or `self.row_data`
        is not completed.`"""
        for column, value in zip(self.header, data):
            self._row_data[column] = value

    def _finalize_row(self):
        """ Finalizes the `self.row_data` update: adds the row data to
        the table, and empties the row data for the next row."""
        row_data = tuple(
            self._row_data.get(label, None) for label in self.header
        )

        self._add_evaluation_step(row_data)
        self._step_metadata.append(self._row_metadata)

        self._row_data = self._row_data_default()
        self._row_metadata = self._row_metadata_default()

    @on_trait_change("header")
    def clear_steps(self):
        """ Removes all entries in the list :attr:`evaluation_steps` and sets
        :attr:`selected_step_indices` to None but does not clear
        :attr:`value_names`
        """
        self._evaluation_steps[:] = []
        self._step_metadata[:] = []
        self._selected_step_indices = None
        self._export_enabled = False

    def _add_evaluation_step(self, evaluation_step):
        """ Add the completed row data to the evaluation steps table.

        Parameters
        ---------
        evaluation_step: tuple
        """
        if len(self.header) == 0:
            raise ValueError(
                "Cannot add evaluation step to an empty Analysis model"
            )

        if len(evaluation_step) != len(self.header):
            raise ValueError(
                "Size of evaluation step is incompatible with the length of "
                "the header."
            )

        self._evaluation_steps.append(evaluation_step)
        self._export_enabled = True

    def column(self, label):
        """ Returns a list of values from the column of the AnalysisModel.
        If `label` is a string, the corresponding column index is inferred
        from the AnalysisModel.header.
        If `label` is an int, it defines the column index."""
        column_error = ValueError(
            f"Column of the AnalysisModel with label {label}"
            " doesn't exist. The label must be a string or int."
        )

        if label in self.header:
            index = self.header.index(label)
        elif isinstance(label, int):
            index = label
        else:
            raise column_error

        if index >= len(self.header):
            raise column_error

        data = [step[index] for step in self.evaluation_steps]
        return data

    def clear(self):
        """ Sets :attr:`value_names` to be empty, removes all entries in the
        list :attr:`evaluation_steps` and sets :attr:`selected_step_indices`
        to None"""
        self.header = self._header_default()

    def from_json(self, data):
        """ Delete all current data and load :attr:`value_names` and
        :attr:`evaluation_steps` from a dictionary.

        """
        self.clear()
        if not data:
            return

        try:
            header = data["header"]
        except KeyError:
            error = (
                "AnalysisModel can't be instantiated from a data dictionary"
                " that does not contain a header."
            )
            log.error(error)
            raise KeyError(error)
        else:
            self.notify(tuple(header))

        for index in range(1, len(data)):
            try:
                step = data[str(index)]
            except KeyError:
                log.warning(
                    f"Can't find a row with index {index}. This index will "
                    f"be skipped in the AnalysisModel."
                )
            else:
                # TODO: This format is now deprecated and should be removed
                #  in version 0.7.0
                #  https://github.com/force-h2020/force-wfmanager/issues/414
                if isinstance(step, list):
                    log.warning(
                        'Project file format is deprecated and will be removed'
                        ' in version 0.7.0')
                    self.notify(step)
                else:
                    self.notify(step['metadata'], metadata=True)
                    self.notify(step['data'])

    def to_json(self):
        """ Returns a dictionary representation with column names as keys
        and column values as values."""
        return self.__getstate__()

    def __getstate__(self):
        """ Returns a dictionary representation with column names as keys
        and column values as values.

        Returns
        -------
        data: a dictionary containing the column-wise representation of
        the `self`.

        """
        data = {"header": self.header}
        for index, row in enumerate(self.evaluation_steps, start=1):
            metadata = self.step_metadata[index-1]
            data[index] = {'data': row, 'metadata': metadata}

        return data

    def write(self, filename, *, mode="w"):
        if filename.endswith(".csv"):
            self.dump_csv(filename, mode=mode)
        elif filename.endswith(".json"):
            self.dump_json(filename, mode=mode)
        else:
            raise IOError(
                "AnalysisModel can only write to .json or .csv formats."
            )

    def dump_json(self, filename, *, mode="w"):
        """ Writes the AnalysisModel to a `filename` file in json format,
        including both data and metadata values. Can be used to save the
        state of the analysis."""
        if not self.export_enabled:
            return False

        with open(filename, mode) as file:
            json.dump(self.__getstate__(), file, indent=4)
        return True

    def dump_csv(self, filename, *, mode="w"):
        """ Writes the AnalysisModel to a `filename` file in csv format,
        but does not include metadata values. Should be only be used to
        export MCO parameter and KPI data, rather than saving the state
        of the analysis.
        """
        if not self.export_enabled:
            return False

        with open(filename, mode) as file:
            writer = csv.writer(file)
            writer.writerow(self.header)
            for step in self.evaluation_steps:
                writer.writerow(step)

        return True
