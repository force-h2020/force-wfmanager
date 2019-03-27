from traits.api import (
    Either, HasStrictTraits, Int, List, Property, Tuple, on_trait_change
)


class AnalysisModel(HasStrictTraits):

    # --------------------
    # Dependent Attributes
    # --------------------

    #: List of parameter names. Set by ``_server_event_mainthread()`` in
    #: :class:`WFManagerSetupTask
    #: <force_wfmanager.wfmanager_setup_task.WfManagerSetupTask>`.
    value_names = Tuple()

    #: Shadow trait of the `evaluation_steps` property
    #: Listens to: :attr:`value_names`
    _evaluation_steps = List(Tuple())

    #: Selected step, used for highlighting in the table/plot.
    #: Listens to: :attr:`value_names`
    _selected_step_indices = Either(None, List(Int()))

    # ----------
    # Properties
    # ----------

    #: Evaluation steps, each evaluation step is a tuple of parameter values,
    #: received from the bdss. Each value can be of any type. The order of
    #: the parameters in each evaluation step must match the order of
    #: value_names
    evaluation_steps = Property(List(Tuple()), depends_on="_evaluation_steps")

    #: Property that informs about the currently selected step.
    #: Can be None if nothing is selected. If selected, it must be
    #: in the allowed range of values.
    #: Listens to :attr:`Plot._plot_index_datasource
    #: <force_wfmanager.central_pane.plot.Plot._plot_index_datasource>`
    selected_step_indices = Property(Either(None, List(Int)),
                                     depends_on="_selected_step_indices")

    @on_trait_change("value_names")
    def _clear_evaluation_steps(self):
        self._evaluation_steps[:] = []
        self._selected_step_indices = None

    def _get_evaluation_steps(self):
        return self._evaluation_steps

    def add_evaluation_step(self, evaluation_step):
        """Add the result of an optimisation run to the AnalysisModel

        Parameters
        ---------
        evaluation_step: Tuple
            A pair of values, which can be of any type.
        """
        if len(self.value_names) == 0:
            raise ValueError("Cannot add evaluation step to an empty "
                             "Analysis model")

        if len(evaluation_step) != len(self.value_names):
            raise ValueError(
                "Size of evaluation step '{}' is incompatible "
                "with the number of value names {}.".format(
                    evaluation_step, self.value_names))

        self._evaluation_steps.append(evaluation_step)

    def _get_selected_step_indices(self):
        return self._selected_step_indices

    def _set_selected_step_indices(self, values):
        self._selected_step_indices = values
        if values is not None:
            for value in values:
                if (isinstance(value, int) and not
                        (0 <= value < len(self._evaluation_steps))):
                    self._selected_step_indices = None
                    raise ValueError(
                        "Invalid value for selection index {}. Current "
                        "number of steps = {}".format(
                            value,
                            len(self._evaluation_steps)
                        )
                    )

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
