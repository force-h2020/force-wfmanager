import re

from traits.api import (
    Dict, Event, HasTraits, Instance, Int, Unicode, provides
)
from traitsui.api import Action, Group, Handler, View

from force_bdss.api import WorkflowReader
from force_wfmanager.ui.contributed_ui.i_contributed_ui import IContributedUI


class ContributedUIHandler(Handler):

    def run_simulation(self, info):
        info.object.run_simulation = True
        self._on_close(info)

    def update_workflow(self, info):
        info.object.update_workflow = True
        self._on_close(info)


@provides(IContributedUI)
class ContributedUI(HasTraits):
    """An object which contains a custom UI for a particular workflow file."""

    #: Name for the UI in selection screen
    name = Unicode()

    #: Description of the UI
    desc = Unicode()

    #: List of plugin ids and versions required for this UI
    required_plugins = Dict(Unicode, Int)

    #: Data for a premade workflow
    workflow_data = Dict()

    #: A Group of Item(s) to show in the UI for this workflow
    workflow_group = Instance(Group)

    #: Event to request a workflow run.
    run_simulation = Event()

    run_simulation_action = Action(
        name="Run Simulation", action="run_simulation"
    )

    #: Event to update a workflow.
    update_workflow = Event()

    update_workflow_action = Action(
        name="Update Workflow", action="update_workflow"
    )

    def default_traits_view(self):
        # Add 'Run Workflow', 'Update Workflow' and 'Cancel' actions as part of
        # the default view.
        return View(
            self.workflow_group,
            buttons=[
                self.run_simulation_action, self.update_workflow_action,
                'Cancel'
            ]
        )

    def create_workflow(self, factory_registry):
        """Create a Workflow from this object's :attr:`workflow_data`

        Parameters
        ----------
        factory_registry: IFactoryRegistry
            The factory registry required by WorkflowReader
        """
        reader = WorkflowReader(factory_registry=factory_registry)
        wf = reader.read_dict(self.workflow_data)
        return wf

    def _required_plugins_default(self):
        plugin_list = search(self.workflow_data, "id")
        required_plugins = {}
        for plugin_id in plugin_list:
            plugin_name, plugin_version = parse_id(plugin_id)
            required_plugins[plugin_name] = plugin_version

        return required_plugins


def search(input, search_term="id", results=None):
    """Search through an input dictionary and return all the matches
    corresponding to a search term

    Parameters
    ----------
    input: Dict
        The input dictionary. In the context of the Workflow Manager, this will
        probably be a json.dump of a workflow file
    search_term: Any
        Anything that can be used as a dictionary key
    results: List, optional
        A list storing the current results. Used when search is called
        recursively e.g. for a dict which has dicts as values.
    """
    if not results:
        # Initial empty results list
        results = []
    if isinstance(input, dict):
        for key, val in input.items():
            if key == "id":
                results.append(val)
            # Search sub-iterables. Note: Don't search stings (even though
            # they are iterables!)
            if isinstance(val, (dict, list, set, tuple)):
                results = search(val, search_term, results)
    elif isinstance(input, (list, set, tuple)):
        for val in input:
            results = search(val, search_term, results)
    return results


def parse_id(id):
    """Parse an id found in json files, which has the form::

    ${plugin_id}.v${version_number}.factory.${factory_name}

    """
    result = re.search(r'(.*)\.v(\d+).*', id)
    plugin_name, plugin_version = result.groups()
    plugin_id = '.'.join([plugin_name, f'v{plugin_version}'])
    return plugin_id, int(plugin_version)
