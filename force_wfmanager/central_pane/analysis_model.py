from traits.api import (
    HasStrictTraits, List, Str, Tuple, Int, on_trait_change, Property, Either
)


class AnalysisModel(HasStrictTraits):
    #: List of parameter names
    value_names = List(Str)

    #: Evaluation steps, each evaluation step is a tuple of parameter values,
    #: received from the bdss. Each value can be of any type. The order of
    #: the parameters in each evaluation step must match the order of
    #: value_names
    evaluation_steps = Property(List(Tuple()), depends_on="_evaluation_steps")

    #: Shadow trait of the above property
    _evaluation_steps = List(Tuple())

    #: Property that informs about the currently selected step.
    #: Can be None if nothing is selected. If selected, it must be
    #: in the allowed range of values.
    selected_step_index = Property(Either(None, Int),
                                   depends_on="_selected_step_index")
    #: Selected step, used for highlighting in the table/plot
    _selected_step_index = Either(None, Int())

    @on_trait_change("value_names[]")
    def _clear_evaluation_steps(self):
        self._evaluation_steps[:] = []
        self._selected_step_index = None

    def _get_evaluation_steps(self):
        return self._evaluation_steps

    def add_evaluation_step(self, evaluation_step):
        if len(self.value_names) == 0:
            raise ValueError("Cannot add evaluation step to an empty "
                             "Analysis model")

        if len(evaluation_step) != len(self.value_names):
            raise ValueError(
                "Size of evaluation step '{}' is incompatible "
                "with the number of value names {}.".format(
                    evaluation_step, self.value_names))

        self._evaluation_steps.append(evaluation_step)

    def _get_selected_step_index(self):
        return self._selected_step_index

    def _set_selected_step_index(self, value):
        if (isinstance(value, int) and not
                (0 <= value < len(self._evaluation_steps))):
            raise ValueError(
                "Invalid value for selection index {}. Current "
                "number of steps = {}".format(
                    value,
                    len(self._evaluation_steps)
                )
            )

        self._selected_step_index = value

    def clear(self):
        self.value_names[:] = []

    def clear_steps(self):
        self._clear_evaluation_steps()
