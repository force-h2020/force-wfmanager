from pyface.tasks.api import TraitsDockPane

from traits.api import Instance, Button, on_trait_change, Bool

from traitsui.api import View, UItem, VGroup

from force_bdss.factory_registry_plugin import FactoryRegistryPlugin
from force_bdss.core.workflow import Workflow

from .workflow_settings import WorkflowSettings


class SidePane(TraitsDockPane):
    """ Side pane which contains the WorkflowSettings (Tree editor for the
    Workflow) and the Run button """
    id = 'force_wfmanager.side_pane'
    name = 'Workflow'

    #: Remove the possibility to close the pane
    closable = False

    #: Remove the possibility to detach the pane from the GUI
    floatable = False

    #: Make the pane visible by default
    visible = True

    #: The factory registry containing all the factories
    factory_registry = Instance(FactoryRegistryPlugin)

    #: The Worflow model
    workflow_m = Instance(Workflow)

    #: Tree editor for the Workflow
    workflow_settings = Instance(WorkflowSettings)

    #: Run button for running the computation
    run_button = Button('Run')

    #: Enable or disable the contained entities.
    #: Used when the computation is running
    enabled = Bool(True)

    traits_view = View(VGroup(
        UItem('workflow_settings',
              style='custom',
              enabled_when="enabled"
              ),
        UItem('run_button',
              enabled_when="enabled"
              )
    ))

    def _workflow_settings_default(self):
        registry = self.factory_registry
        kpi_calculator_factories = registry.kpi_calculator_factories
        return WorkflowSettings(
            available_mco_factories=registry.mco_factories,
            available_data_source_factories=registry.data_source_factories,
            available_kpi_calculator_factories=kpi_calculator_factories,
            workflow_m=self.workflow_m)

    @on_trait_change('workflow_m', post_init=True)
    def update_workflow_settings(self, *args, **kwargs):
        self.workflow_settings.workflow_m = self.workflow_m
