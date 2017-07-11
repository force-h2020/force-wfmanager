from pyface.tasks.api import TraitsTaskPane
from traitsui.api import View, UItem, Tabbed
from traits.api import Instance

from configuration import Configuration
from analysis import Analysis


class CentralPane(TraitsTaskPane):
    id = 'wfmanager.central_pane'
    name = 'Central Pane'

    configuration = Instance(Configuration, ())
    analysis = Instance(Analysis, ())

    view = View(Tabbed(
        UItem('configuration', style='custom'),
        UItem('analysis', style='custom')
    ))
