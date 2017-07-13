from pyface.tasks.api import TraitsDockPane
from traitsui.api import View, Item, Tabbed
from traits.api import List


class WorkflowSettings(TraitsDockPane):
    id = 'force_wfmanager.workflow_settings'
    name = 'Plugins'

    available_mcos = List()
    available_kpis = List()

    # Those values are created by the user on the UI, the user will be
    # able to set the constraint name and parameters
    constraints = List(['Constraint1', 'Constraint2', 'Constraint3'])

    # Those values will come from the plugins
    mcos = List()
    kpis = List()

    view = View(Tabbed(
        Item('mcos', label='MCO'),
        Item('constraints', label='Constraints'),
        Item('kpis'),
        ))

    def _mcos_default(self):
        return [mco.name for mco in self.available_mcos]

    def _kpis_default(self):
        return [kpi.computes for kpi in self.available_kpis]
