import json
import logging

from traits.api import (
    Bool,
    Str,
    Either,
    HasStrictTraits,
    Int,
    List,
    Property,
    Tuple,
    on_trait_change,
)

log = logging.getLogger(__name__)


class NewAnalysisModel(HasStrictTraits):

    #: Tuple of column names of the analysis model. The names are defined
    #: by the MCOStartEvent parsed in ``_server_event_mainthread()`` in
    #: :class:`WFManagerSetupTask
    #: <force_wfmanager.wfmanager_setup_task.WfManagerSetupTask>`.
    value_names = Tuple(Str())

    #: Shadow trait of the `evaluation_steps` property
    #: Listens to: :attr:`value_names`
    _evaluation_steps = List(Tuple())

    #: Tracks whether the current state of AnalysisModel can be exported
    _export_enabled = Bool(False)

    #: Evaluation steps, each evaluation step is a tuple of parameter values,
    #: received from the bdss. Each value can be of any type. The order of
    #: the parameters in each evaluation step must match the order of
    #: value_names
    evaluation_steps = Property(List(Tuple()), depends_on="_evaluation_steps")

    #: If there are results, then they can be exported
    export_enabled = Property(Bool(), depends_on="_export_enabled")

    #: Selected step, used for highlighting in the table/plot.
    #: Listens to: :attr:`value_names`
    _selected_step_indices = Either(None, List(Int()))

    #: Property that informs about the currently selected step.
    #: Can be None if nothing is selected. If selected, it must be
    #: in the allowed range of values.
    #: Listens to :attr:`Plot._plot_index_datasource
    #: <force_wfmanager.central_pane.plot.Plot._plot_index_datasource>`
    selected_step_indices = Property(
        Either(None, List(Int)), depends_on="_selected_step_indices"
    )

    # ------------------
    #     Listeners
    # ------------------

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
        if values is not None:
            for value in values:
                if isinstance(value, int) and not (
                    0 <= value < len(self._evaluation_steps)
                ):
                    raise ValueError(
                        "Invalid value for selection index {}. Current "
                        "number of steps = {}".format(
                            value, len(self._evaluation_steps)
                        )
                    )

        self._selected_step_indices = values

    @on_trait_change("value_names")
    def _clear_evaluation_steps(self):
        self._evaluation_steps[:] = []
        self._selected_step_indices = None
        self._export_enabled = False

    # ------------------
    #   Public Methods
    # ------------------

    def add_evaluation_step(self, evaluation_step):
        """Add the result of an optimisation run to the AnalysisModel

        Parameters
        ---------
        evaluation_step: Tuple
            A pair of values, which can be of any type.
        """
        if len(self.value_names) == 0:
            raise ValueError(
                "Cannot add evaluation step to an empty Analysis model"
            )

        if len(evaluation_step) != len(self.value_names):
            raise ValueError(
                "Size of evaluation step '{}' is incompatible "
                "with the number of value names {}.".format(
                    evaluation_step, self.value_names
                )
            )

        self._evaluation_steps.append(evaluation_step)
        self._export_enabled = True

    def clear(self):
        """ Sets :attr:`value_names` to be empty, removes all entries in the
        list :attr:`evaluation_steps` and sets :attr:`selected_step_indices`
        to None"""
        self.value_names = ()
        self._clear_evaluation_steps()

    def clear_steps(self):
        """ Removes all entries in the list :attr:`evaluation_steps` and sets
        :attr:`selected_step_indices` to None but does not clear
        :attr:`value_names`
        """
        self._clear_evaluation_steps()

    def from_dict(self, data):
        """ Delete all current data and load :attr:`value_names` and
        :attr:`evaluation_steps` from a dictionary.

        """
        self._clear_evaluation_steps()
        self.value_names = tuple(data.keys())
        if not self.value_names:
            return
        for ind, _ in enumerate(data[self.value_names[0]]):
            step = tuple(data[column][ind] for column in self.value_names)
            self.add_evaluation_step(step)

    def as_json(self):
        """ Returns a JSON representation with column names as keys and
        values stored as lists under those keys.

        Returns
        -------
        dict: a dictionary containing the JSON representation.

        """
        json_representation = {}
        for name in self.value_names:
            json_representation[name] = []
        for step in self.evaluation_steps:
            for ind, name in enumerate(self.value_names):
                json_representation[name].append(step[ind])

        return json_representation

    def write_to_json(self, fp):
        """ Write the current state of the AnalysisModel to a file in JSON format.

        Parameters
        ----------
        fp (a .write() supporting file-like object).

        Returns
        -------
        bool: whether the write was successful or not.

        """
        if not self._export_enabled:
            return False

        json.dump(self.as_json(), fp, sort_keys=False, indent=4)

        return True

    def write_to_csv(self, fp):
        """ Write the current state of the AnalysisModel to a file in a CSV format,
        that includes column names in the first line.

        Parameters
        ----------
        fp (a .write() supporting file-like object).

        Returns
        -------
        bool: whether the write was successful or not.

        """
        if not self._export_enabled:
            return False

        fp.write(", ".join(self.value_names) + "\n")
        for step in self.evaluation_steps:
            # val can have arbitrary type, so cannot
            # e.g. specify a floating point precision
            fp.write(", ".join([str(val) for val in step]) + "\n")

        return True
