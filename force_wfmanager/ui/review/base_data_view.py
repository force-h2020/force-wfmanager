#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

import logging

from pyface.timer.api import CallbackTimer
from traits.api import (
    Bool,
    Instance,
    HasStrictTraits,
    List,
    Callable,
    provides,
    on_trait_change
)

from force_wfmanager.model.analysis_model import AnalysisModel

from .i_data_view import IDataView

log = logging.getLogger(__name__)


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

    #: Timer to check on required updates
    plot_updater = Instance(CallbackTimer)

    #: Schedule a refresh of plot data and axes. Set to True
    #: by default: the plot needs to be refreshed if the
    #: MCO was started from the 'Setup' pane.
    update_required = Bool(True)

    def _displayable_data_mask_default(self):
        """ Default mask for data coming from the analysis model.
        Verifies that the data entry is numerical value."""

        def is_numerical(data_entry):
            return isinstance(data_entry, (int, float))

        return is_numerical

    def _plot_updater_default(self):
        return CallbackTimer.timer(
            interval=1, callback=self._check_scheduled_updates
        )

    @on_trait_change("analysis_model:evaluation_steps[]")
    def request_update(self):
        # Listens to the change in data points in the analysis model.
        # Enables the plot update at the next cycle.
        self.update_required = True

    @on_trait_change("is_active_view")
    def toggle_updater_with_visibility(self):
        """Start/stop the update if this data view is not being used. """
        if self.is_active_view:
            if not self.plot_updater.active:
                self.plot_updater.start()
            self.update_required = True
            self._check_scheduled_updates()
        elif self.plot_updater.active:
            self.plot_updater.stop()
            log.warning("Stopped plot updater")

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
        if (
            len(self.analysis_model.evaluation_steps) == 0
            or len(self.analysis_model.header) == 0
        ):
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

    def _check_scheduled_updates(self):
        """ Update the data view if an update was required. This function
        is a callback for the _plot_updater timer.
        """
        if self.update_required:
            self._update_displayable_value_names()
            self.update_data_view()
            self.update_required = False

    def update_data_view(self):
        """Perform customized updates for data view. Should be made into
        an abstract method in later versions
        """
