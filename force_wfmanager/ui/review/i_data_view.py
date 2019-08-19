from traits.api import Interface, Instance

from force_wfmanager.model.analysis_model import AnalysisModel


class IDataView(Interface):
    """Envisage required interface for the BaseDataView class.
    You should not need to use this directly.

    Refer to the BaseDataView for documentation.
    """

    #: The analysis model containing the results
    analysis_model = Instance(AnalysisModel)
