from pyface.tasks.api import TraitsTaskPane
from traitsui.api import View


class Analysis(TraitsTaskPane):
    id = 'force_wfmanager.analysis'
    name = 'Analysis'

    view = View()
