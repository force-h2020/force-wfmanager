from traits.api import Instance,  List, on_trait_change, Str, Event

from traitsui.api import (
    TreeEditor, TreeNode, UItem, View, Menu, Action, ModelView, UReadonly,
    VGroup, TextEditor
)


from force_bdss.api import verify_workflow, VerifierError
from force_bdss.core.kpi_specification import KPISpecification
from force_bdss.core.workflow import Workflow
from force_bdss.factory_registry_plugin import IFactoryRegistryPlugin
from force_wfmanager.left_side_pane.data_source_model_view import \
    DataSourceModelView
from force_wfmanager.left_side_pane.execution_layer_model_view import \
    ExecutionLayerModelView

from force_bdss.core.execution_layer import ExecutionLayer

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
        refresh="update_event"
    )

    #: The workflow model
    model = Instance(Workflow, allow_none=False)

    #: The workflow model view
    workflow_mv = Instance(WorkflowModelView, allow_none=False)

    #: List of verification errors in this view
    verification_errors = List(Instance(VerifierError))

    #: Available MCO factories
    _factory_registry = Instance(IFactoryRegistryPlugin)

    #: The currently selected modelview
    selected_mv = Instance(ModelView)

    #: The error message relating to selected_mv
    selected_error = Str

    #: An event which runs a verification chack on the current workflow
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

    def _workflow_mv_default(self):
        return WorkflowModelView(model=self.model)

    def _verify_workflow_event_fired(self):
        result = verify_workflow(self.model)
        self.verification_errors = result

    @on_trait_change('model')
    def update_model_view(self):
        self.workflow_mv.model = self.model

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

    @on_trait_change("verification_errors")
    def print_errors(self):

        verification_subj = [v.subject for v in self.verification_errors]
        verification_error = {v.subject: v.error for v
                              in self.verification_errors}

        parent_child = {WorkflowModelView: ['mco_mv',
                                            'notification_listeners_mv',
                                            'execution_layers_mv'],
                        MCOModelView: ['mco_parameters_mv', 'kpis_mv'],
                        ExecutionLayerModelView: ['data_sources_mv']}
        self.verify_tree(self.workflow_mv, parent_child,
                         verification_subj, verification_error)

    @staticmethod
    def verify_tree(mv_list, mappings, error_subjects, error_messages):
        """ Call with a list of modelview objects to assign
        their error messages, plus the error message of
        their subsequent child modelviews.

        :param mv_list
        A list of ModelViews
        :param mappings
        A dict containing the names of child modelview lists,
        for each type of modelview
        :param error_subjects
        The model instances containing errors, from verifier.py
        :param error_messages
        The error messages associated to the subjects in error_subjects
        """

        if not isinstance(mv_list, list):
            mv_list = [mv_list]

        # If you have any children, call this function for them
        for modelview in mv_list:
            modelview.error_message = ''
            for type, lists in mappings.items():
                if isinstance(modelview, type):
                    for child_mv_list_name in lists:
                        child_mv_list = getattr(modelview, child_mv_list_name)
                        child_errors = WorkflowTree.verify_tree(child_mv_list,
                                                                mappings,
                                                                error_subjects,
                                                                error_messages)
                        modelview.error_message += child_errors
                        if modelview.error_message != '':
                            modelview.valid = False

        errors_from_list = ''

        for modelview in mv_list:
            if modelview.model in error_subjects:
                modelview.error_message += (error_messages[modelview.model] +
                                            '\n')
            if modelview.error_message != '':
                modelview.valid = False
            else:
                modelview.valid = True

            errors_from_list += modelview.error_message
        return errors_from_list
