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
from force_wfmanager.ui.setup.process.data_source_view \
    import DataSourceView
from force_wfmanager.ui.setup.process.execution_layer_view \
    import ExecutionLayerView

from force_wfmanager.ui.setup.new_entity_creator import NewEntityCreator
from force_wfmanager.ui.setup.process.process_view import ProcessView
from force_wfmanager.ui.ui_utils import model_info
from force_wfmanager.utils.variable_names_registry import (
    VariableNamesRegistry
)
from force_wfmanager.ui.setup.system_state import SystemState
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

    process_view = Instance(ProcessView, allow_none=False)

    #: A registry of the available factories
    _factory_registry = Instance(IFactoryRegistry)

    #: A class that holds the temporary state of the UI
    system_state = Instance(SystemState)

    # ------------------
    # Regular Attributes
    # ------------------

    #: The ModelView currently selected in the ProcessTree. Updated
    #: automatically when a new ModelView is selected by the user
    selected_view = Either(Instance(HasTraits), Instance(ModelView))

    # ----------
    # Properties
    # ----------

    #: The error message currently displayed in the UI.
    selected_error = Property(
        Unicode(),
        depends_on="selected_view.[error_message,label]"
    )

    def default_traits_view(self):
        """The layout of the View for the ProcessTree"""
        print('default_traits_view called')
        tree_editor = TreeEditor(
            nodes=[
                # Root node "Workflow"
                TreeNodeWithStatus(
                    node_for=[ProcessView],
                    auto_open=True,
                    children='',
                    name='Process',
                    label='=Process',
                    view=no_view,
                    menu=no_menu,
                    on_select=self.system_state.workflow_selected
                ),

                #: Node representing the Execution layers
                TreeNode(
                    node_for=[ProcessView],
                    auto_open=True,
                    children='execution_layer_views',
                    label='=Execution Layers',
                    name='Execution Layers',
                    view=no_view,
                    menu=Menu(new_layer_action),
                    on_select=partial(
                        self.system_state.factory,
                        None,
                        self.new_layer,
                        'Execution Layer'
                    )
                ),
                TreeNodeWithStatus(
                    node_for=[ExecutionLayerView],
                    auto_open=True,
                    children='data_source_views',
                    label='label',
                    name='DataSources',
                    view=no_view,
                    menu=Menu(delete_layer_action),
                    on_select=partial(
                        self.system_state.factory_instance,
                        self._factory_registry.data_source_factories,
                        self.new_data_source,
                        'Data Source',
                        self.delete_layer
                    )
                ),
                TreeNodeWithStatus(
                    node_for=[DataSourceView],
                    auto_open=True,
                    children='',
                    label='label',
                    name='DataSources',
                    menu=Menu(delete_data_source_action),
                    on_select=partial(self.system_state.instance,
                                      self.delete_data_source)
                )
            ],
            orientation="horizontal",
            editable=False,
            selected="selected_view",
        )

        view = View(
            Group(
                VGroup(
                    UItem(name='process_view',
                          editor=tree_editor,
                          show_label=False
                          )
                )
            ),
            width=500,
            resizable=True,
        )

        return view

    @on_trait_change('selected_view')
    def sync_selected_mv(self):
        self.system_state.selected_mv = self.selected_view

    # Methods for new entity creation - The args ui_info and object
    # (the selected modelview) are passed by the ProcessTree on selection.
    # Additional (unused) args are passed when calling dclick_function by
    # double-clicking a specific factory in the NewEntityCreator
    def new_data_source(self, ui_info, object, *args):
        """Adds a new datasource to the workflow."""
        object.add_data_source(self.system_state.entity_creator.model)
        self.system_state.entity_creator.reset_model()
        self.process_view.verify_workflow_event = True

    def new_layer(self, ui_info, object):
        """Adds a new execution layer to the workflow"""
        self.process_view.add_execution_layer(ExecutionLayer())
        self.process_view.verify_workflow_event = True

    # Methods for deleting entities from the workflow - object is the
    # modelview being deleted.
    # E.g. for delete_data_source the object is a DataSourceModelView

    def delete_data_source(self, ui_info, object):
        """Delete a data source from the workflow"""
        self.process_view.remove_data_source(object.model)
        self.process_view.verify_workflow_event = True

    def delete_layer(self, ui_info, object):
        """Delete a execution layer from the workflow"""
        self.process_view.remove_execution_layer(object.model)
        self.process_view.verify_workflow_event = True

    # Workflow Verification
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
        print('process_tree _get_selected_error called')
        if self.selected_view is None:
            return ERROR_TEMPLATE.format("No Item Selected", "")

        if self.selected_view.error_message == '':
            mv_label = self.selected_view.label
            return ERROR_TEMPLATE.format(
                "No errors for {}".format(mv_label), "")
        else:
            mv_label = self.selected_view.label
            error_list = self.selected_view.error_message.split('\n')
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
