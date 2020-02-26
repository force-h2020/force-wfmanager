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
)
from force_bdss.local_traits import PositiveInt

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

    #: Private trait of the `evaluation_steps` property
    _evaluation_steps = List(Tuple())

    #: Evaluation steps, each evaluation step is a tuple of parameter values,
    #: received from the a single Worjflow execution. The order of
    #: the parameters in each evaluation step must match the order of
    #: value_names
    evaluation_steps = Property(List(Tuple()), depends_on="_evaluation_steps")

    #: Tracks whether the current state of AnalysisModel can be exported
    _export_enabled = Bool(False)

    #: If there are results, then they can be exported
    export_enabled = Property(Bool(), depends_on="_export_enabled")

    #: Selected step, used for highlighting in the table/plot.
    #: If selected, it must be in the allowed range of values.
    _selected_step_indices = Either(None, List(PositiveInt()))

    #: Property that informs about the currently selected step.
    selected_step_indices = Property(
        Either(None, List(PositiveInt)), depends_on="_selected_step_indices"
    )

    def _header_default(self):
        return ()

    def _row_data_default(self):
        return dict.fromkeys(self.header)

    def _get_export_enabled(self):
        return self._export_enabled

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
            if value > len(self.evaluation_steps):
                raise ValueError(
                    f"Invalid value for selection index {value}. "
                    "It must be a positive Int less or equal to "
                    f"{len(self.evaluation_steps)-1}"
                )

        self._selected_step_indices = values

    def notify(self, data):
        """ Public method to add `data` to the AnalysisModel.
        If no `header` is set up, the `data` is considered to be a
        `header`. Otherwise, the `data` is treated as to be added to
        the current row.
        """
        if not self.header:
            self._add_header(data)
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
        self._row_data = self._row_data_default()

    def clear_steps(self):
        """ Removes all entries in the list :attr:`evaluation_steps` and sets
        :attr:`selected_step_indices` to None but does not clear
        :attr:`value_names`
        """
        self._evaluation_steps[:] = []
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

    def clear(self):
        """ Sets :attr:`value_names` to be empty, removes all entries in the
        list :attr:`evaluation_steps` and sets :attr:`selected_step_indices`
        to None"""
        self.header = self._header_default()
        self.clear_steps()

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
                step = data[index]
            except KeyError:
                log.warning(
                    f"Can't find a row with index {index}. This index will "
                    f"be skipped in the AnalysisModel."
                )
            else:
                self.notify(step)

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
            data[index] = row

        return data

    def dump_json(self, filename, *, mode="w"):
        """ Writes the AnalysisModel to a `filename` file in json format."""
        if not self.export_enabled:
            return False

        with open(filename, mode) as file:
            json.dump(self.__getstate__(), file, indent=4)
        return True

    def dump_csv(self, filename, *, mode="w"):
        """ Writes the AnalysisModel to a `filename` file in csv format."""
        if not self.export_enabled:
            return False

        with open(filename, mode) as file:
            writer = csv.writer(file)
            writer.writerow(self.header)
            for step in self.evaluation_steps:
                writer.writerow(step)

        return True
