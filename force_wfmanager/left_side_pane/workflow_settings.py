from pyface.tasks.api import TraitsDockPane
from traitsui.api import (View, Item, VGroup, Tabbed, SetEditor, EnumEditor,
                          Handler)
from traits.api import Enum, List, Str


class KpiHandler(Handler):
    kpis = List(Str)

    def object_kpis_changed(self, info):
        self.kpis = info.object.kpis
        info.object.selected_kpi = '' if not len(self.kpis) else self.kpis[0]


class WorkflowSettings(TraitsDockPane):
    id = 'force_wfmanager.workflow_settings'
    name = 'Plugins'

    # Those values will come from the plugins
    mcos = Enum(
        ['Dakota', 'MCO2', 'MCO3', 'MCO4'])

    # Those values are created by the user on the UI, the user will be
    # able to set the constraint name and parameters
    constraints = List(
        ['Constraint1', 'Constraint2', 'Constraint3'])

    # Those values will come from the plugins
    kpis = List(editor=SetEditor(
        values=['Viscosity', 'Cost', 'Incomes'],
        can_move_all=True,
        left_column_title='Available KPIs',
        right_column_title='KPIs'))

    selected_kpi = Str

    view = View(Tabbed(
        Item('mcos', label='MCO'),
        Item('constraints', label='Constraints'),
        VGroup(
            Item('kpis'),
            Item('selected_kpi',
                 editor=EnumEditor(name='handler.kpis')),
            label='KPIs')),
        handler=KpiHandler)
