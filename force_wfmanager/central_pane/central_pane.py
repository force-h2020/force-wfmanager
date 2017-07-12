from pyface.tasks.api import TraitsTaskPane
from traitsui.api import View, UItem
from traits.api import Instance

from analysis import Analysis


class CentralPane(TraitsTaskPane):
    id = 'wfmanager.central_pane'
    name = 'Central Pane'

    analysis = Instance(Analysis, ())

    view = View(
        UItem('analysis', style='custom')
    )
