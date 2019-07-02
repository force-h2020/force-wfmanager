from functools import partial, wraps

from traits.api import (
    Callable, Event, Instance, Property, Unicode, on_trait_change,
    cached_property, Either, HasTraits
)
from traitsui.api import (
    Action, Group, Menu, ModelView,
    TreeEditor, TreeNode, UItem, View, VGroup
)

from force_bdss.api import (
    ExecutionLayer, IFactoryRegistry
)
from force_wfmanager.ui.setup.process.data_source_model_view \
    import DataSourceModelView
from force_wfmanager.ui.setup.process.execution_layer_model_view \
    import ExecutionLayerModelView

from force_wfmanager.ui.setup.new_entity_creator import NewEntityCreator
from force_bdss.core.process import Process
from force_wfmanager.ui.setup.process.process_model_view import ProcessModelView
from force_wfmanager.ui.ui_utils import model_info
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)
from force_wfmanager.ui.setup.workflow_model_view import WorkflowModelView

# VerifierError severity constants
_ERROR = "error"
_WARNING = "warning"
_INFO = "information"


# Create an empty view and menu for objects that have no data to display:
no_view = View()
no_menu = Menu()

# -------------------
# Actions!
# -------------------

# Execution Layer Actions
new_layer_action = Action(name="New Layer...", action='new_layer')
delete_layer_action = Action(name='Delete', action='delete_layer')

# DataSource Actions
delete_data_source_action = Action(name='Delete', action='delete_data_source')

def selection(func):
    """ Decorator for functions called on selecting something in the tree
    editor. Clears the `selected_factory_name`, `entity_creator`,
    `add_new_entity` and `remove_entity` attributes before they are set
    based on the selection choice
    """
    @wraps(func)
    def wrap(self, *args, **kwargs):
        self.selected_factory_name = 'None'
        self.entity_creator = None
        self.add_new_entity = None
        self.remove_entity = None
        func(self, *args, **kwargs)
    return wrap


class TreeNodeWithStatus(TreeNode):
    """ Custom TreeNode class for workflow elements. Allows setting a
    workflow element's icon depending on whether it has an error or not.
    """

    def get_icon(self, object, is_expanded):
        """ Overrides get_icon method of TreeNode.

        Parameters
        ----------
        object: ModelView
            The ModelView assigned to this TreeNode
        is_expanded: bool
            True if the TreeNode is expanded, i.e. child nodes of this
            TreeNode are also visible in the UI.
        """
        return 'icons/valid.png' if object.valid else 'icons/invalid.png'

    def when_label_changed(self, object, listener, remove):
        """ Overrides/Extends when_label_change method of TreeNode.
        This method sets up the listener as normal, where it responds to
        changes in the TreeNode label. Additionally, it sets the listener
        to respond to changes in the 'valid' attribute of a ModelView.

        Parameters
        ----------
        object: ModelView
            The ModelView assigned to this TreeNode
        listener: method
            The _label_updated method from TreeEditor
        remove: bool
            Whether to remove the listener from object

        Notes
        -----
        This is done as the method label_updated in tree_editor.py is one of
        the few handler methods to call update_icon. Since we also want to
        update the icon in response to a property change, this is a logical
        place to add the extra functionality.
        Unfortunately, the calls take place at the toolkit (qt, wx) level
        rather than at traitsUI level so this can't be done more directly.
        """
        super(TreeNodeWithStatus, self).when_label_changed(
            object, listener, remove
        )
        object.on_trait_change(listener, 'valid')


class ProcessTree(HasTraits):
    """ Part of the GUI containing the tree editor displaying the Workflow."""

    # -------------------
    # Required Attributes
    # -------------------

    process_model_view = Instance(ProcessModelView, allow_none=False)

    #: A registry of the available factories
    _factory_registry = Instance(IFactoryRegistry)

    # ------------------
    # Regular Attributes
    # ------------------

    #: A View containing the UI elements for this class
    traits_view = View()

    #: The ModelView currently selected in the ProcessTree. Updated
    #: automatically when a new ModelView is selected by the user
    selected_mv = Either(Instance(HasTraits), Instance(ModelView))

    # ------------------
    # Derived Attributes
    # ------------------

    #: The factory currently selected in the TreePane
    selected_factory_name = Unicode()

    #: Creates new instances of DataSource, MCO, Notification Listener or
    #: MCO Parameters - depending on the plugins currently installed.
    #: Listens to: :func:`~selected_mv`
    entity_creator = Instance(NewEntityCreator)

    #: A method which adds the new instance from entity_creator to the
    #: appropriate place in the Workflow.
    #: Listens to: :func:`~selected_mv`
    add_new_entity = Callable()

    #: A method which removes the currently selected instance from the
    #: Workflow.
    #: Listens to: :func:`~selected_mv`
    remove_entity = Callable()

    #: An event which runs a verification check on the current workflow when
    #: triggered.
    #: Listens to: :func:`~workflow_mv.verify_workflow_event`
    verify_workflow_event = Event

    # ----------
    # Properties
    # ----------

    #: The error message currently displayed in the UI.
    selected_error = Property(
        Unicode(),
        depends_on="selected_mv.[error_message,label]"
    )

    def default_traits_view(self):
        """The layout of the View for the ProcessTree"""
        print('default_traits_view called')
        tree_editor = TreeEditor(
            nodes=[
                # Root node "Workflow"
                TreeNodeWithStatus(
                    node_for=[ProcessModelView],
                    auto_open=True,
                    children='',
                    name='Process',
                    label='=Process',
                    view=no_view,
                    menu=no_menu,
                    on_select=self.workflow_selected
                ),

                #: Node representing the Execution layers
                TreeNode(
                    node_for=[ProcessModelView],
                    auto_open=True,
                    children='execution_layer_model_views',
                    label='=Execution Layers',
                    name='Execution Layers',
                    view=no_view,
                    menu=Menu(new_layer_action),
                    on_select=partial(
                        self.factory,
                        None,
                        self.new_layer,
                        'Execution Layer'
                    )
                ),
                TreeNodeWithStatus(
                    node_for=[ExecutionLayerModelView],
                    auto_open=True,
                    children='data_source_model_views',
                    label='label',
                    name='DataSources',
                    view=no_view,
                    menu=Menu(delete_layer_action),
                    on_select=partial(
                        self.factory_instance,
                        self._factory_registry.data_source_factories,
                        self.new_data_source,
                        'Data Source',
                        self.delete_layer
                    )
                ),
                TreeNodeWithStatus(
                    node_for=[DataSourceModelView],
                    auto_open=True,
                    children='',
                    label='label',
                    name='DataSources',
                    menu=Menu(delete_data_source_action),
                    on_select=partial(self.instance, self.delete_data_source)
                )
            ],
            orientation="horizontal",
            editable=False,
            selected="selected_mv",
        )

        view = View(
            Group(
                VGroup(
                    UItem(name='process_model_view',
                          editor=tree_editor,
                          show_label=False
                          )
                )
            ),
            width=500,
            resizable=True,
        )

        return view

    @on_trait_change('process_model_view', post_init=True)
    def update_model_view(self):
        """Update the workflow modelview's model and verify, on either loading
        a new workflow, or an internal change to the workflow.
        """
        self.verify_workflow_event = True

    # Item Selection Actions - create an appropriate NewEntityModal,
    # set add_new_entity to be for the right object type and provide a way to
    # add things by double clicking

    @selection
    def factory_instance(self, from_registry, create_fn, factory_group_name,
                         delete_fn, modelview):
        """Called on selecting a node in the TreeEditor which represents an
        instance in the workflow, but also represents a factory for creating
        new instances.
        For example an ExecutionLayerModelView represents an ExecutionLayer
        object, but is also a factory for new DataSources.

        Parameters
        ----------
        from_registry: List(BaseFactory) or Callable
            A list of factories available for this node
        create_fn: function
            A function which adds a newly created instance to the Workflow
        factory_group_name: String
            A name showing which group (MCO, Datasource etc.) the factory
            belongs to
        delete_fn: function
            A function which removes the object from the workflow
        modelview: ModelView
            The modelview of the currently selected node
        """

        self.factory.__wrapped__(self, from_registry, create_fn,
                                 factory_group_name, modelview)
        self.instance.__wrapped__(self, delete_fn, modelview)

    @selection
    def factory(self, from_registry, create_fn, factory_group_name, modelview):
        """Called on selecting a node in the TreeEditor which represents a
        factory.

        Parameters
        ----------
        from_registry: List(BaseFactory) or Callable
            A list of factories available for this node
        create_fn: function
            A function which adds a newly created instance to the Workflow
        factory_group_name: String
            A name showing which group (MCO, Datasource etc.) the factory
            belongs to
        modelview: ModelView
            The modelview of the currently selected node
        """
        self.add_new_entity = partial(create_fn, None, modelview)
        if from_registry is not None:
            try:
                # For a non-constant factory list (parameter factories)
                visible_factories = [
                    f for f in from_registry() if f.ui_visible
                ]
            except TypeError:
                visible_factories = [f for f in from_registry if f.ui_visible]
            entity_creator = NewEntityCreator(
                factories=visible_factories,
                dclick_function=self.add_new_entity
            )
            self.entity_creator = entity_creator
        else:
            self.entity_creator = None
        self.selected_factory_name = factory_group_name

    @selection
    def instance(self, delete_fn, modelview):
        """Called on selecting a a node in the TreeEditor which represents an
        object in the workflow

        Parameters
        ----------
        delete_fn: function
            A function which removes the object from the workflow
        modelview: ModelView
            The modelview of the currently selected node
        """

        self.remove_entity = partial(delete_fn, None, modelview)

    @selection
    def workflow_selected(self, workflow_mv):
        """Called on selecting the top node in the ProcessTree

        Parameters
        ----------
        workflow_mv: WorkflowModelView
            Unused, automatically passed by TreeEditor on selection
        """
        self.selected_factory_name = 'Workflow'

    # Methods for new entity creation - The args ui_info and object
    # (the selected modelview) are passed by the ProcessTree on selection.
    # Additional (unused) args are passed when calling dclick_function by
    # double-clicking a specific factory in the NewEntityCreator

    def new_data_source(self, ui_info, object, *args):
        """Adds a new datasource to the workflow."""
        object.add_data_source(self.entity_creator.model)
        self.entity_creator.reset_model()
        self.verify_workflow_event = True

    def new_layer(self, ui_info, object):
        """Adds a new execution layer to the workflow"""
        self.process_model_view.add_execution_layer(ExecutionLayer())
        self.verify_workflow_event = True

    # Methods for deleting entities from the workflow - object is the
    # modelview being deleted.
    # E.g. for delete_data_source the object is a DataSourceModelView

    def delete_data_source(self, ui_info, object):
        """Delete a data source from the workflow"""
        self.process_model_view.remove_data_source(object.model)
        self.verify_workflow_event = True

    def delete_layer(self, ui_info, object):
        """Delete a execution layer from the workflow"""
        self.process_model_view.remove_execution_layer(object.model)
        self.verify_workflow_event = True

    # Workflow Verification

    @on_trait_change("process_model_view.verify_workflow_event")
    def received_verify_request(self):
        """Checks if the root node of workflow tree is requesting a
        verification of the workflow"""
        self.verify_workflow_event = True

    def modelview_editable(self, modelview):
        """Checks if the model associated to a ModelView instance
        has a non-empty, editable view

        Parameters
        ----------
        modelview: ModelView
            A ModelView
        """
        return model_info(modelview.model) != []

    @cached_property
    def _get_selected_error(self):
        """Returns the error messages for the currently selected modelview"""
        if self.selected_mv is None:
            return ERROR_TEMPLATE.format("No Item Selected", "")

        if self.selected_mv.error_message == '':
            mv_label = self.selected_mv.label
            return ERROR_TEMPLATE.format(
                "No errors for {}".format(mv_label), "")
        else:
            mv_label = self.selected_mv.label
            error_list = self.selected_mv.error_message.split('\n')
            body_strings = ''.join([SINGLE_ERROR.format(error)
                                    for error in error_list])
            return ERROR_TEMPLATE.format(
                "Errors for {}:".format(mv_label), body_strings)


# HTML Formatting Templates
ERROR_TEMPLATE = """
    <html>
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
        <style type="text/css">
            .container{{
                width: 100%;
                font-family: sans-serif;
                display: block;
            }}
        </style>
    </head>
    <body>
    <h4>{}</h4>
        {}
    </body>
    </html>
"""

SINGLE_ERROR = r"""<p>{}<\p>"""
