from pyface.tasks.api import TraitsDockPane
from traitsui.api import View, Item, VGroup, SetEditor, ListStrEditor
from traits.api import List


class PluginManager(TraitsDockPane):
    id = 'wfmanager.plugin_manager'
    name = 'Plugins'

    multi_criteria_optimizers_editor = ListStrEditor(
        editable=False,
        multi_select=False
    )

    multi_criteria_optimizers = List(
        ['Dakota', 'MCO2', 'MCO3', 'MCO4'],
        editor=multi_criteria_optimizers_editor)

    key_perfomance_indicators = List(editor=SetEditor(
        values=['Viscosity', 'Cost', 'Incomes'],
        can_move_all=True,
        left_column_title='Available KPIs',
        right_column_title='KPIs'))

    view = View(VGroup(
        Item('multi_criteria_optimizers'),
        Item('key_perfomance_indicators')
    ))
