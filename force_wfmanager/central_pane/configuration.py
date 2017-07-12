from pyface.tasks.api import TraitsTaskPane
from traitsui.api import View, Item
from traits.api import Enum


class Configuration(TraitsTaskPane):
    id = 'wfmanager.configuration'
    name = 'Configuration'

    # Example on how to put elements in the UI
    constraint_type = Enum('=', '>', '<', '<=', '>=')

    view = View(Item('constraint_type'))
