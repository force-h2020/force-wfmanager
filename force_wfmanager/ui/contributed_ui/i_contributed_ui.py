from traits.api import Dict, Event, Instance, Int, Interface, Str
from traitsui.api import Action, Group


class IContributedUI(Interface):
    """Interface definition for the ContributedUI class. Instructions
    for how to contribute additional UI objects can be found in
    the force-bdss documentation.

    Key attributes required by any sublcass using this interface
    are listed below. A `create_workflow` method is also required
    to be implemented, which generates a `Workflow` object."""

    #: Name for the UI in selection screen
    name = Str()

    #: Description of UI
    desc = Str()

    #: List of plugin ids and versions required for this UI
    required_plugins = Dict(Str, Int)

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
