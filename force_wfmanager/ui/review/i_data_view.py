from traits.api import Interface, Instance, Bool

from force_wfmanager.model.new_analysis_model import AnalysisModel


class IDataView(Interface):
    """Interface definition for the BaseDataView class. Instructions
    for how to contribute additional UI objects can be found in
    the force-bdss documentation.

    Subclasses using this interface require an `analysis_model`
    attribute that contains data to be displayed, and an
    `is_active_view` attribute for communication with WfManager
    UI."""

    #: The analysis model containing the results
    analysis_model = Instance(AnalysisModel)

    #: Whether this data view is the one being currently visualized
    is_active_view = Bool(False)
