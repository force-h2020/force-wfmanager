#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

from chaco.api import ArrayDataSource
from traits.api import Instance

from .i_data_view import IDataView


class IBasePlot(IDataView):
    """Interface definition for the BasePlot class. Instructions
    for how to contribute additional UI objects can be found in
    the force-bdss documentation.

    Subclasses using this interface currently require a
    `_plot_index_datasource` attribute in order to access
    the data to be displayed and a `_plot_default` method
    to be implemented in order to instruct how to display it.

    Note - it is expect that these requirements be expanded
    upon during further development of the UI"""

    #: Listens to: :attr:`analysis_model.selected_step_indices
    #: <force_wfmanager.model.analysis_model.AnalysisModel.\
    #: selected_step_indices>`
    _plot_index_datasource = Instance(ArrayDataSource)

    def __plot_default(self):
        raise NotImplementedError
