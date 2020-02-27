from traits.api import (
    Bool,
    Instance,
    HasStrictTraits,
    List,
    Callable,
    provides,
)

from force_wfmanager.model.new_analysis_model import AnalysisModel


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

    #: A list of displayable columns from the analysis model's value names
    displayable_value_names = List()

    #: a Callable: object -> Bool that indicates if the object
    #: can be displayed by the BasePlot instance.
    displayable_data_mask = Callable()

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

        if len(self.analysis_model.header) == 0:
            self.displayable_value_names[:] = []
            return

        evaluation_step = self.analysis_model.evaluation_steps[-1]

        masked_value_names = [
            name
            for (value, name) in zip(
                evaluation_step, self.analysis_model.header
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
