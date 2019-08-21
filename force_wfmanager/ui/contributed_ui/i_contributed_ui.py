from traits.api import Dict, Event, Instance, Int, Interface, Unicode
from traitsui.api import Action, Group


class IContributedUI(Interface):
    """Envisage required interface for the ContributedUI class.
    You should not need to use this directly.

    Refer to the ContributedUI for documentation.
    """

    #: Name for the UI in selection screen
    name = Unicode()

    #: Description of UI
    desc = Unicode()

    #: List of plugin ids and versions required for this UI
    required_plugins = Dict(Unicode, Int)

    #: Data for a premade workflow
    workflow_data = Dict()

    #: A Group of Item(s) to show in the UI for this workflow
    workflow_group = Instance(Group)

    #: Event to request a workflow run.
    run_simulation = Event

    run_simulation_action = Action

    #: Event to update a workflow.
    update_workflow = Event

    update_workflow_action = Action

    def create_workflow(self, factory_registry):
        """Returns a Workflow object populated with the required MCO,
        datasource and notification listener models"""
        raise NotImplementedError
