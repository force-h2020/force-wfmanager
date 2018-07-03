import re
from difflib import SequenceMatcher

from traits.api import Instance, on_trait_change, Str, Event

from traitsui.api import (
    TreeEditor, TreeNode, UItem, View, Menu, Action, ModelView, UReadonly,
    VGroup, TextEditor
)

from force_bdss.api import (KPISpecification, Workflow, IFactoryRegistryPlugin,
                            ExecutionLayer, verify_workflow)

from force_wfmanager.left_side_pane.data_source_model_view import \
    DataSourceModelView
from force_wfmanager.left_side_pane.execution_layer_model_view import \
    ExecutionLayerModelView

# Create an empty view and menu for objects that have no data to display:
from force_wfmanager.left_side_pane.kpi_specification_model_view import \
    KPISpecificationModelView
from force_wfmanager.left_side_pane.mco_model_view import MCOModelView
from force_wfmanager.left_side_pane.mco_parameter_model_view import \
    MCOParameterModelView
from force_wfmanager.left_side_pane.new_entity_modal import NewEntityModal
from force_wfmanager.left_side_pane.notification_listener_model_view import \
    NotificationListenerModelView
from force_wfmanager.left_side_pane.workflow_model_view import \
    WorkflowModelView


no_view = View()
no_menu = Menu()

# Actions!
new_mco_action = Action(name='New MCO...', action='new_mco')
delete_mco_action = Action(name='Delete', action='delete_mco')
edit_mco_action = Action(name='Edit...', action='edit_mco')

new_notification_listener_action = Action(
    name='New Notification Listener...',
    action='new_notification_listener')
delete_notification_listener_action = Action(
    name='Delete',
    action='delete_notification_listener')
edit_notification_listener_action = Action(
    name='Edit...',
    action='edit_notification_listener')
new_parameter_action = Action(name='New Parameter...', action='new_parameter')
edit_parameter_action = Action(name='Edit...', action='edit_parameter')
delete_parameter_action = Action(name='Delete', action='delete_parameter')
new_kpi_action = Action(name='New KPI...', action='new_kpi')
delete_kpi_action = Action(name="Delete", action='delete_kpi')
new_layer_action = Action(name="New Layer...", action='new_layer')
delete_layer_action = Action(name='Delete', action='delete_layer')
new_data_source_action = Action(name='New DataSource...',
                                action='new_data_source')
delete_data_source_action = Action(name='Delete', action='delete_data_source')
edit_data_source_action = Action(name='Edit...', action='edit_data_source')


#: Wrapper to call workflow verification after each method
def verify(func):
    def wrap(self, *args, **kwargs):
        func(self, *args, **kwargs)
        self.verify_workflow_event = True
    return wrap


class TreeNodeWithStatus(TreeNode):
    """ Custom TreeNode class for workflow elements """

    def get_icon(self, object, is_expanded):
        return 'icons/valid.png' if object.valid else 'icons/invalid.png'

    original_label_changed = TreeNode.when_label_changed

    def when_label_changed(self, object, listener, remove):
        self.original_label_changed(object, listener, remove)
        object.on_trait_change(listener, 'valid')


class WorkflowTree(ModelView):
    """ Part of the GUI containing the tree editor displaying the Workflow """

    tree_editor = TreeEditor(
        nodes=[
            # Root node "Workflow"
            TreeNodeWithStatus(
                node_for=[WorkflowModelView],
                auto_open=True,
                children='',
                label='=Workflow',
                view=no_view,
                menu=no_menu,
            ),
            # Folder node "Notification" containing the Notification listeners
            TreeNode(
                node_for=[WorkflowModelView],
                auto_open=True,
                children='notification_listeners_mv',
                label='=Notification Listeners',
                view=no_view,
                menu=Menu(new_notification_listener_action),
            ),
            # Node representing the Notification Listener
            TreeNodeWithStatus(
                node_for=[NotificationListenerModelView],
                auto_open=True,
                children='',
                label='label',
                view=no_view,
                menu=Menu(edit_notification_listener_action,
                          delete_notification_listener_action),
            ),
            # Folder node "MCO" containing the MCO
            TreeNode(
                node_for=[WorkflowModelView],
                auto_open=True,
                children='mco_mv',
                label='=MCO',
                view=no_view,
                menu=Menu(new_mco_action),
            ),
            # Node representing the MCO
            TreeNodeWithStatus(
                node_for=[MCOModelView],
                auto_open=True,
                children='',
                label='label',
                view=no_view,
                menu=Menu(edit_mco_action, delete_mco_action),
            ),
            # Folder node "Parameters" containing the MCO parameters
            TreeNode(
                node_for=[MCOModelView],
                auto_open=True,
                children='mco_parameters_mv',
                label='=Parameters',
                view=no_view,
                menu=Menu(new_parameter_action),
            ),
            #: Node representing an MCO parameter
            TreeNodeWithStatus(
                node_for=[MCOParameterModelView],
                auto_open=True,
                children='',
                label='label',
                menu=Menu(edit_parameter_action, delete_parameter_action),
            ),
            TreeNode(
                node_for=[MCOModelView],
                auto_open=True,
                children='kpis_mv',
                label='=KPIs',
                view=no_view,
                menu=Menu(new_kpi_action),
            ),
            TreeNodeWithStatus(
                node_for=[KPISpecificationModelView],
                auto_open=True,
                children='',
                label='label',
                menu=Menu(delete_kpi_action),
            ),
            #: Node representing the layers
            TreeNode(
                node_for=[WorkflowModelView],
                auto_open=True,
                children='execution_layers_mv',
                label='=Execution Layers',
                view=no_view,
                menu=Menu(new_layer_action),
            ),
            TreeNodeWithStatus(
                node_for=[ExecutionLayerModelView],
                auto_open=True,
                children='data_sources_mv',
                label='label',
                view=no_view,
                menu=Menu(new_data_source_action, delete_layer_action),
            ),
            TreeNodeWithStatus(
                node_for=[DataSourceModelView],
                auto_open=True,
                children='',
                label='label',
                menu=Menu(edit_data_source_action, delete_data_source_action),
            ),
        ],
        orientation="vertical",
        selected="selected_mv",
    )

    #: The workflow model
    model = Instance(Workflow, allow_none=False)

    #: The workflow model view
    workflow_mv = Instance(WorkflowModelView, allow_none=False)

    #: Available MCO factories
    _factory_registry = Instance(IFactoryRegistryPlugin)

    #: The currently selected modelview
    selected_mv = Instance(ModelView)

    #: The error message relating to selected_mv
    selected_error = Str

    #: An event which runs a verification check on the current workflow
    verify_workflow_event = Event

    traits_view = View(
        VGroup(
            UItem(name='workflow_mv',
                  editor=tree_editor,
                  show_label=False
                  ),
            UReadonly(
                name='selected_error',
                editor=TextEditor(),
                ),
            ),
        width=800,
        height=600,
        resizable=True
        )

    def __init__(self, model, factory_registry, *args, **kwargs):
        super(WorkflowTree, self).__init__(*args, **kwargs)
        self.model = model
        self._factory_registry = factory_registry

    def _workflow_mv_default(self):
        return WorkflowModelView(model=self.model)

    @on_trait_change('model')
    def update_model_view(self):
        """Update the workflow modelview's model and verify, on either loading
        a new workflow, or an internal change to the workflow"""
        self.workflow_mv.model = self.model
        self.verify_workflow_event = True

    @verify
    def new_mco(self, ui_info, object):
        """ Opens a dialog for creating a MCO """
        workflow_mv = self.workflow_mv

        modal = NewEntityModal(factories=self._factory_registry.mco_factories)
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            workflow_mv.set_mco(result)

    @verify
    def edit_mco(self, ui_info, object):
        object.model.edit_traits(kind="livemodal")

    @verify
    def delete_mco(self, ui_info, object):
        """Deletes the MCO"""
        self.workflow_mv.set_mco(None)

    @verify
    def new_notification_listener(self, ui_info, object):
        """ Opens a dialog for creating a notification listener"""
        workflow_mv = self.workflow_mv

        visible_factories = [
            f for f in self._factory_registry.notification_listener_factories
            if f.ui_visible
        ]
        modal = NewEntityModal(
            factories=visible_factories
        )
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            workflow_mv.add_notification_listener(result)

    @verify
    def edit_notification_listener(self, ui_info, object):
        object.model.edit_traits(kind="livemodal")

    @verify
    def delete_notification_listener(self, ui_info, object):
        """Deletes the notification listener"""
        self.workflow_mv.remove_notification_listener(object.model)

    @verify
    def new_parameter(self, ui_info, object):
        parameter_factories = []
        if self.model.mco is not None:
            parameter_factories = self.model.mco.factory.parameter_factories()

        modal = NewEntityModal(factories=parameter_factories)
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            object.add_parameter(result)

    @verify
    def edit_parameter(self, ui_info, object):
        object.model.edit_traits(kind="livemodal")

    @verify
    def delete_parameter(self, ui_info, object):
        if len(self.workflow_mv.mco_mv) > 0:
            mco_mv = self.workflow_mv.mco_mv[0]
            mco_mv.remove_parameter(object.model)

    @verify
    def new_kpi(self, ui_info, object):
        object.add_kpi(KPISpecification())

    @verify
    def delete_kpi(self, ui_info, object):
        if len(self.workflow_mv.mco_mv) > 0:
            mco_mv = self.workflow_mv.mco_mv[0]
            mco_mv.remove_kpi(object.model)

    @verify
    def new_data_source(self, ui_info, object):
        """ Opens a dialog for creating a Data Source """
        modal = NewEntityModal(
            factories=self._factory_registry.data_source_factories
        )
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            object.add_data_source(result)

    @verify
    def delete_data_source(self, ui_info, object):
        self.workflow_mv.remove_data_source(object.model)

    @verify
    def edit_data_source(self, ui_info, object):
        # This is a live dialog, workaround for issue #58
        object.model.edit_traits(kind="livemodal")

    @verify
    def new_layer(self, ui_info, object):
        self.workflow_mv.add_execution_layer(ExecutionLayer())

    @verify
    def delete_layer(self, ui_info, object):
        """ Delete an element from the workflow """
        self.workflow_mv.remove_execution_layer(object.model)

    @on_trait_change("selected_mv,verify_workflow_event")
    def update_selected_error(self):
        if self.selected_mv is None:
            self.selected_error = 'No errors'
        elif self.selected_mv.error_message == '':
            self.selected_error = 'No errors'
        else:
            self.selected_error = self.selected_mv.error_message

    @on_trait_change("workflow_mv.verify_workflow_event")
    def received_verify_request(self):
        """Checks if the root node of workflow tree is requesting a
        verification of the workflow"""
        self.verify_workflow_event = True

    def _verify_workflow_event_fired(self):
        """Verify the workflow and update the modelviews in the workflow tree
        with any errors"""
        result = verify_workflow(self.model)
        parent_child = {WorkflowModelView: ['mco_mv',
                                            'notification_listeners_mv',
                                            'execution_layers_mv'],
                        MCOModelView: ['mco_parameters_mv', 'kpis_mv'],
                        ExecutionLayerModelView: ['data_sources_mv']}
        verify_tree(self.workflow_mv, parent_child, result)


def verify_tree(mv_list, mappings, errors):
    """ Call with a list of modelview objects to assign
    their error messages, plus the error message of
    their subsequent child modelviews.

    :param mv_list
    A list of ModelViews
    :param mappings
    A dict containing the names of child modelview lists,
    for each type of modelview
    :param errors
    A list of VerifierError, where object.error is an error message and
    object.subject is the component of the workflow it applies to
    """
    if not isinstance(mv_list, list):
        mv_list = [mv_list]

    for modelview in mv_list:
        modelview.error_message = ''
        for type, lists in mappings.items():
            if isinstance(modelview, type):
                for child_mv_list_name in lists:
                    child_mv_list = getattr(modelview, child_mv_list_name)
                    child_errors = verify_tree(child_mv_list,
                                               mappings,
                                               errors)
                    modelview.error_message += child_errors
                    if modelview.error_message != '':
                        modelview.valid = False

    errors_from_list = ''

    for modelview in mv_list:
        for error_pair in errors[:]:
            if modelview.model == error_pair.subject:
                error_string = error_pair.error
                modelview.error_message += (error_string + '\n')
                errors.remove(error_pair)

        if modelview.error_message != '':
            modelview.valid = False
        else:
            modelview.valid = True
        modelview.error_message = collate_errors(modelview.error_message)
        errors_from_list += modelview.error_message

    return errors_from_list


def collate_errors(error_message):
    """Populates a dictionary where each key is a different type of error. The
    value is an index by which they can be grouped"""

    #: List of error messages
    error_list = error_message.split('\n')
    #: Dict with similar errors grouped together
    group_errors = {}

    def ignore(error_1, error_2):
        """Pairs which definitely should not be in grouped strings"""
        ignore_pairs = [["input", "output"]]
        both_strings = error_1+' '+error_2
        for pair in ignore_pairs:
            if pair[0] in both_strings and pair[1] in both_strings:
                return True
        return False

    #: Build a dict of error groups and indexes which share an error type
    for error in error_list:
        match = False
        digit_regexp = re.search(r'\d+', error)
        if digit_regexp is not None:
            index = digit_regexp.group()
        else:
            index = None
        for key in group_errors:
            s = SequenceMatcher(None, key, error)

            if ignore(error, key) is True:
                pass
            elif s.ratio() > 0.9:
                match = True
                group_errors[key].append(index)
        if match is False:
            group_errors[error] = [index]

    #: Format a string from the dict of error groups
    return_string = ''
    for key, value in group_errors.items():
        if None not in value:
            repl = ''
            if len(value) == 1:
                repl = value[0]
            elif abs(int(value[-1]) - int(value[0])) == len(value)-1:
                repl = '{}-{}'.format(min(value[0], value[-1]), max(value[0],
                                                                    value[-1]))
            else:
                repl = ','.join(value)

            return_string += re.sub(r'\d+', repl, key, count=1)
            return_string += '\n'
        else:
            return_string += key
            return_string += '\n'

    return return_string
