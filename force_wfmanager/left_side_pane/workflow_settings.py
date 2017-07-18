from pyface.tasks.api import TraitsDockPane
from traitsui.api import ListStrEditor, Tabbed, UItem, View
from traitsui.list_str_adapter import ListStrAdapter
from traits.api import List, Instance


class ListAdapter(ListStrAdapter):
    def get_text(self, object, trait, index):
        return self.item.name


class WorkflowSettings(TraitsDockPane):
    id = 'force_wfmanager.workflow_settings'
    name = 'Plugins'

    available_mcos = List()
    available_data_sources = List()

    selected_mco = Instance('force_bdss.mco.i_multi_criteria_optimizer_bundle.'
                            'IMultiCriteriaOptimizerBundle')
    selected_data_source = Instance('force_bdss.data_sources.'
                                    'i_data_source_bundle.IDataSourceBundle')

    view = View(Tabbed(
        UItem(
            "available_mcos",
            editor=ListStrEditor(
                adapter=ListAdapter(),
                selected="selected_mco"),
            label='MCOs',
        ),
        UItem(
            'available_data_sources',
            editor=ListStrEditor(
                adapter=ListAdapter(),
                selected="selected_data_source"),
            label='Data Sources'
        )
    ))
