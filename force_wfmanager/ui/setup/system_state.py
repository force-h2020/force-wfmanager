from functools import partial, wraps

from traits.api import (
    HasTraits, Either, Instance, Unicode, Property, Callable
)
from traitsui.api import ModelView

from force_bdss.api import BaseFactory

from force_wfmanager.ui.setup.new_entity_creator import NewEntityCreator


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


class SystemState(HasTraits):

    #: The ModelView currently selected in the Side Pane. Updated
    #: automatically when a new ModelView is selected by the user
    selected_view = Either(Instance(HasTraits), Instance(ModelView))

    selected_factory = Instance(BaseFactory)

    #: The factory currently selected in the TreePane
    selected_factory_name = Unicode()

    #: Creates new instances of DataSource, MCO, Notification Listener or
    #: MCO Parameters - depending on the plugins currently installed.
    #: Listens to: :func:`~selected_view`
    entity_creator = Instance(NewEntityCreator)

    #: A function which adds a new entity to the workflow tree, using the
    #: currently selected factory. For example, if the 'DataSources' factory
    #: is selected, this function would be ``new_data_source()``.
    #: Listens to: :attr:`models.process_tree.add_new_entity
    #: <force_wfmanager.models.process_tree.WorkflowTree.\
    #: add_new_entity>`
    add_new_entity = Callable()

    #: A function to remove the currently selected modelview from the
    #: workflow tree.
    #: Listens to: :attr:`models.process_tree.remove_entity
    #: <force_wfmanager.models.process_tree.WorkflowTree.\
    #: remove_entity>`
    remove_entity = Callable()

    selected_error = Property(
        Unicode(),
        depends_on="selected_view.[error_message,label]"
    )

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