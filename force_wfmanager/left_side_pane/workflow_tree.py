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
def verify_wkflow(func):
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

    @verify_wkflow
    def new_mco(self, ui_info, object):
        """ Opens a dialog for creating a MCO """
        workflow_mv = self.workflow_mv

        modal = NewEntityModal(factories=self._factory_registry.mco_factories)
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            workflow_mv.set_mco(result)

    @verify_wkflow
    def edit_mco(self, ui_info, object):
        object.model.edit_traits(kind="livemodal")

    @verify_wkflow
    def delete_mco(self, ui_info, object):
        """Deletes the MCO"""
        self.workflow_mv.set_mco(None)

    @verify_wkflow
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

    @verify_wkflow
    def edit_notification_listener(self, ui_info, object):
        object.model.edit_traits(kind="livemodal")

    @verify_wkflow
    def delete_notification_listener(self, ui_info, object):
        """Deletes the notification listener"""
        self.workflow_mv.remove_notification_listener(object.model)

    @verify_wkflow
    def new_parameter(self, ui_info, object):
        parameter_factories = []
        if self.model.mco is not None:
            parameter_factories = self.model.mco.factory.parameter_factories()

        modal = NewEntityModal(factories=parameter_factories)
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            object.add_parameter(result)

    @verify_wkflow
    def edit_parameter(self, ui_info, object):
        object.model.edit_traits(kind="livemodal")

    @verify_wkflow
    def delete_parameter(self, ui_info, object):
        if len(self.workflow_mv.mco_mv) > 0:
            mco_mv = self.workflow_mv.mco_mv[0]
            mco_mv.remove_parameter(object.model)

    @verify_wkflow
    def new_kpi(self, ui_info, object):
        object.add_kpi(KPISpecification())

    @verify_wkflow
    def delete_kpi(self, ui_info, object):
        if len(self.workflow_mv.mco_mv) > 0:
            mco_mv = self.workflow_mv.mco_mv[0]
            mco_mv.remove_kpi(object.model)

    @verify_wkflow
    def new_data_source(self, ui_info, object):
        """ Opens a dialog for creating a Data Source """
        modal = NewEntityModal(
            factories=self._factory_registry.data_source_factories
        )
        modal.edit_traits()
        result = modal.current_model

        if result is not None:
            object.add_data_source(result)

    @verify_wkflow
    def delete_data_source(self, ui_info, object):
        self.workflow_mv.remove_data_source(object.model)

    @verify_wkflow
    def edit_data_source(self, ui_info, object):
        # This is a live dialog, workaround for issue #58
        object.model.edit_traits(kind="livemodal")

    @verify_wkflow
    def new_layer(self, ui_info, object):
        self.workflow_mv.add_execution_layer(ExecutionLayer())

    @verify_wkflow
    def delete_layer(self, ui_info, object):
        """ Delete an element from the workflow """
        self.workflow_mv.remove_execution_layer(object.model)

    @on_trait_change("selected_mv")
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

    @on_trait_change("verify_workflow_event")
    def perform_verify_workflow_event_(self):
        """Verify the workflow and update error_message traits of
        every ModelView in the workflow"""

        errors = verify_workflow(self.model)

        # A (currently hardcoded) dictionary with the mappings between
        # modelview lists
        parent_child = {'WorkflowModelView': ['mco_mv',
                                              'notification_listeners_mv',
                                              'execution_layers_mv'],
                        'MCOModelView': ['mco_parameters_mv', 'kpis_mv'],
                        'ExecutionLayerModelView': ['data_sources_mv']}

        # Communicate the verification errors to each level of the
        # workflow tree
        self.verify_tree(parent_child, errors)

        # Update the message displayed in the TreeEditor, as the change
        # which triggered verify_workflow_event may have created new errors
        # or resolved existing errors
        self.update_selected_error()

    def verify_tree(self, mappings, errors, current_modelview=None):
        """ Assign the errors generated by verifier.py to the appropriate
        ModelView. Parent ModelViews also have the error messages from
        their child ModelViews"""

        if current_modelview is None:
            current_modelview = self.workflow_mv

        current_modelview.error_message = ''
        current_modelview_type = current_modelview.__class__.__name__

        if current_modelview_type in mappings:
            # Call self.verify_tree for any child modelviews, retrieving their
            # error messages.
            for child_modelview_list_name in mappings[current_modelview_type]:

                child_modelview_list = getattr(current_modelview,
                                               child_modelview_list_name)

                for child_modelview in child_modelview_list:
                    child_modelview_errors = self.verify_tree(mappings, errors,
                                                              child_modelview)
                    current_modelview.error_message += child_modelview_errors
                    if current_modelview.error_message != '':
                        current_modelview.valid = False

        # Check current_modelview for errors
        for error_pair in errors:
            if current_modelview.model == error_pair.subject:
                error_string = error_pair.error
                current_modelview.error_message += (error_string + '\n')

        if current_modelview.error_message != '':
            current_modelview.valid = False
            # Combine errors which refer to similar problems
            current_modelview.error_message = collate_errors(current_modelview.
                                                             error_message)
        else:
            current_modelview.valid = True

        return current_modelview.error_message


def collate_errors(error_message):
    """Group together similar error messages. For example, if output
    parameters 1,2 and 3 have undefined names display 'Output parameters 1-3
    have undefined names', rather than 3 separate error messages."""

    #: List of error messages
    error_list = error_message.split('\n')

    #: Dict with similar errors grouped together
    group_errors = {}

    #: Keywords which indicate two separate errors should not be collated,
    #: even when they are otherwise similar
    ignore_pairs = [["input", "output"], ["Name", "Type"]]

    def ignore_func(ignore_pair_list):
        def wrap(error_1, error_2):
            for pair in ignore_pair_list:
                check = (pair[0] in error_1 and pair[1] in error_2) or (
                            pair[1] in error_1 and pair[0] in error_2)
                if check is True:
                    return True
            return False
        return wrap

    ignore = ignore_func(ignore_pairs)

    #: Build a dict where keys are error messages and values are the indexes
    #: from similar error messages.
    for error in error_list:
        match = False
        # A regexp used to give the first number appearing in an error message
        digit_regexp = re.search(r'\d+', error)

        if digit_regexp is not None:
            index = digit_regexp.group()
        else:
            index = None

        for key in group_errors:
            # A measure of similarity between previous error messages and
            # this one
            s = SequenceMatcher(None, key, error)

            if ignore(error, key) is True:
                pass
            elif s.ratio() > 0.9:
                match = True
                group_errors[key].append(index)

        if match is False:
            group_errors[error] = [index]

    #: Format a string for each entry in group_errors
    return_string = ''
    for key, value in group_errors.items():
        # Errors with an index == None cannot be sensibly combined, so just
        # leave them as they are
        if None not in value:
            # Single, consecutive or non-consecutive
            if len(value) == 1:
                repl = value[0]
            elif abs(int(value[-1]) - int(value[0])) == len(value)-1:
                repl = '{}-{}'.format(min(value[0], value[-1]),
                                      max(value[0], value[-1]))
            else:
                repl = ','.join(value)

            return_string += re.sub(r'\d+', repl, key, count=1)
            return_string += '\n'
        else:
            return_string += key
            return_string += '\n'

    return return_string
