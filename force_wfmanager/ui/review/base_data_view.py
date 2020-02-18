from traits.api import (
    Bool, Instance, HasStrictTraits, List, Callable, provides
)

from force_wfmanager.model.analysis_model import AnalysisModel

from .i_data_view import IDataView


@provides(IDataView)
class BaseDataView(HasStrictTraits):
    """ Base class for contributed UI views of models. """

    #: The analysis model containing the results
    analysis_model = Instance(AnalysisModel, allow_none=False)

    #: Whether this data view is the one being currently visualized
    is_active_view = Bool(False)

    #: Short description for the UI selection (to be overwritten)
    description = "Base Data View"

    #: List containing the data arrays from the
    #: analysis_mode.evaluation steps.
    data_arrays = List(List())

    #: A list of displayable columns from the analysis model's value names
    displayable_value_names = List()

    #: a Callable: object -> Bool that indicates if the object
    #: can be displayed by the BasePlot instance.
    displayable_data_mask = Callable()

    def _data_arrays_default(self):
        return [[] for _ in range(len(self.analysis_model.value_names))]

    def _displayable_data_mask_default(self):
        """ Default mask for data coming from the analysis model.
        Verifies that the data entry is numerical value."""
        def is_numerical(data_entry):
            return isinstance(data_entry, (int, float))
        return is_numerical

    def _update_displayable_value_names(self):
        """ This method is a part of the `_check_scheduled_updates`
        callback function.
        Updates the list of the `_displayable_value_names`.
        If the analysis model doesn't have any data in `_evaluation_steps`,
        the _displayable_value_names list should be empty as we can't infer
        the data type.

        If the _displayable_value_names list is empty, we accept all value
        names from the model, whose corresponding columns contain only
        entries fulfilling `self.displayable_data_mask(entry) == True`.
        If an evaluation step contains data that can't be displayed by the
        current plot (`self.displayable_data_mask(entry) == False`), then
        that value name is removed from `self._displayable_value_names`.
        """
        if len(self.analysis_model.evaluation_steps) == 0:
            self.displayable_value_names[:] = []
            return

        if len(self.analysis_model.value_names) == 0:
            self.displayable_value_names[:] = []
            return

        evaluation_step = self.analysis_model.evaluation_steps[-1]

        masked_value_names = [
            name
            for (value, name) in zip(
                evaluation_step, self.analysis_model.value_names
            )
            if self.displayable_data_mask(value)
        ]

        if len(self.displayable_value_names) == 0:
            _displayable_value_names = masked_value_names
        else:
            _displayable_value_names = [
                name
                for name in masked_value_names
                if name in self.displayable_value_names
            ]
        # If the evaluation step changes (reduces) the number of
        # displayable columns, we update the `self.numerical_value_names`.
        if len(self.displayable_value_names) != len(_displayable_value_names):
            self.displayable_value_names[:] = _displayable_value_names

    def _update_data_arrays(self):
        """ This method is a part of the `_check_scheduled_updates`
        callback function.
        Update the data arrays used by the plot. It assumes that the
        AnalysisModel object is valid. Which means that the number of
        value_names is equal to the number of element in each evaluation step
        (e.g. value_names=["viscosity", "pressure"] then each evaluation step
        is a two dimensions tuple). Only the number of evaluation
        steps can change, not their values.

        Note: evaluation steps is row-based (one tuple = one row). The data
        arrays are column based. The transformation happens here.
        """
        data_dim = len(self.analysis_model.value_names)

        # If there is no data yet, or the data has been removed, make sure the
        # plot is updated accordingly (empty arrays)
        if data_dim == 0:
            self.data_arrays = self._data_arrays_default()
            return

        # In this case, the value_names have changed, so we need to
        # synchronize the number of data arrays to the newly found data
        # dimensionality before adding new data to them. Of course, this also
        # means to remove the current content.
        if data_dim != len(self.data_arrays):
            self.data_arrays = self._data_arrays_default()

        evaluation_steps = self.analysis_model.evaluation_steps.copy()

        # If the number of evaluation steps is less than the number of element
        # in the data arrays, it certainly means that the model has been
        # reinitialized. The only thing we can do is recompute the data arrays.
        if len(evaluation_steps) < len(self.data_arrays[0]):
            for data_array in self.data_arrays:
                data_array[:] = []

        # Update the data arrays with the newly added evaluation_steps
        new_evaluation_steps = evaluation_steps[len(self.data_arrays[0]):]
        for evaluation_step in new_evaluation_steps:
            # Fan out the data in the appropriate arrays. The model guarantees
            # that the size of the evaluation step and the data_dim are the
            # same.
            for index in range(data_dim):
                self.data_arrays[index].append(evaluation_step[index])
