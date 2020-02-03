from traits.api import (
    HasTraits, Instance, Str, Callable
)

from force_wfmanager.ui.setup.new_entity_creator import NewEntityCreator


class SystemState(HasTraits):

    # ------------------
    # Regular Attributes
    # ------------------

    #: The ModelView currently selected in the Side Pane. Updated
    #: automatically when a new ModelView is selected by the user
    selected_view = Instance(HasTraits)

    #: The factory currently selected in the TreePane
    selected_factory_name = Str('None')

    #: Creates new instances of DataSource, MCO, Notification Listener or
    #: MCO Parameters - depending on the plugins currently installed.
    entity_creator = Instance(NewEntityCreator)

    #: A function which adds a new entity to the workflow tree, using the
    #: currently selected factory. For example, if the 'DataSources' factory
    #: is selected, this function would be ``new_data_source()``.
    add_new_entity = Callable()

    #: A function to remove the currently selected modelview from the
    #: workflow tree.
    remove_entity = Callable()
