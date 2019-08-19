from chaco.api import ArrayDataSource
from traits.api import Instance

from .i_data_view import IDataView


class IBasePlot(IDataView):
    """Envisage required interface for the BasePlot class.
    You should not need to use this directly.

    Refer to the BasePlot for documentation.
    """

    #: Listens to: :attr:`analysis_model.selected_step_indices
    #: <force_wfmanager.model.analysis_model.AnalysisModel.\
    #: selected_step_indices>`
    _plot_index_datasource = Instance(ArrayDataSource)

    def __plot_default(self):
        raise NotImplementedError
