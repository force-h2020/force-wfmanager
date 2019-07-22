from traits.api import (
    Instance, Unicode, Bool, on_trait_change, Event, Property,
    cached_property, HasTraits, List, Button
)
from traitsui.api import (
    View, Item, HGroup, ModelView, ListEditor, VGroup, InstanceEditor
)

from force_bdss.api import BaseMCOParameter, BaseMCOModel

from force_wfmanager.ui.setup.new_entity_creator import NewEntityCreator
from force_wfmanager.ui.ui_utils import get_factory_name


class MCOParameterModelView(ModelView):

    # -------------------
    # Required Attributes
    # -------------------

    #: MCO parameter model
    model = Instance(BaseMCOParameter)

    # --------------------
    # Dependent Attributes
    # --------------------

    #: Defines if the MCO parameter is valid or not. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    valid = Bool(True)

    #: An error message for issues in this modelview. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    error_message = Unicode()

    #: Event to request a verification check on the workflow
    #: Listens to: :attr:`model.name <model>` and :attr:`model.type <model>`
    verify_workflow_event = Event

    # -----------------
    #     Properties
    # -----------------

    #: The human readable name of the MCO parameter class
    label = Property(Unicode(), depends_on="model.[name,type]")

    # ---------------
    #      View
    # ----------------

    def default_traits_view(self):
        """Default view containing both traits from the base class and
        any additional user-defined traits"""

        return View(Item('name', object='model'),
                    Item('type', object='model'),
                    Item('model',
                         editor=InstanceEditor(),
                         style='custom')
                    )

    # -------------------
    #      Defaults
    # -------------------

    def _label_default(self):
        """Return a default label corresponding to the MCO parameter factory"""
        return get_factory_name(self.model.factory)

    # -------------------
    #     Listeners
    # -------------------

    @cached_property
    def _get_label(self):
        """Return a label appending both the parameter name and type to the
        default"""
        if self.model.name == '' and self.model.type == '':
            return self._label_default()
        return self._label_default()+': {type} {name}'.format(
            type=self.model.type, name=self.model.name
        )

    # Workflow Validation
    @on_trait_change('model.[name,type]')
    def parameter_change(self):
        """Alert to a change in the model"""
        self.verify_workflow_event = True


class MCOParameterView(HasTraits):

    # -------------------
    # Required Attributes
    # -------------------

    #: MCO model
    model = Instance(BaseMCOModel)

    # -------------------
    # Regular Attributes
    # -------------------

    #: List of MCO parameter model views
    parameter_model_views = List(Instance(MCOParameterModelView))

    # --------------------
    # Dependent Attributes
    # --------------------

    #: The selected parameter model view
    selected_parameter = Instance(MCOParameterModelView)

    #: Creates new instances of MCO Parameters
    parameter_entity_creator = Instance(NewEntityCreator)

    #: Defines if the MCO parameter is valid or not. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    valid = Bool(True)

    #: An error message for issues in this modelview. Updated by
    #: :func:`verify_tree
    #: <force_wfmanager.ui.setup.workflow_tree.WorkflowTree.verify_tree>`
    error_message = Unicode()

    #: Event to request a verification check on the workflow
    #: Listens to: :attr:`parameter_model_views.verify_workflow_event
    #: <MCOParameterModelView>`
    verify_workflow_event = Event()

    # -----------------
    #     Properties
    # -----------------

    #: The human readable name of the MCOParameterView class
    label = Unicode('MCO Parameters')

    # ------------------
    #      Buttons
    # ------------------

    #: Button to add a new parameter to the MCO using the
    #: parameter_entity_creator
    add_parameter_button = Button('New Parameter')

    #: Button to remove selected_parameter from the MCO
    remove_parameter_button = Button('Delete Parameter')

    # ------------------
    #       View
    # ------------------

    def default_traits_view(self):
        """Creates a traits view containing a notebook list of existing MCO
        parameters above an entity creator from which the user can select new
        parameter types"""

        # Defines a list editor to display parameter_model_views
        parameter_editor = ListEditor(
            page_name='.label',
            use_notebook=True,
            dock_style='tab',
            selected='selected_parameter')

        traits_view = View(
            VGroup(
                #: Displays existing parameters
                VGroup(
                    Item('parameter_model_views',
                         editor=parameter_editor,
                         show_label=False,
                         style='custom',
                         ),
                    show_labels=False,
                    show_border=True
                ),
                #: Displays new parameter creator
                HGroup(
                    Item(
                        "parameter_entity_creator",
                        editor=InstanceEditor(),
                        style="custom",
                        show_label=False
                    ),
                    springy=True,
                ),
                HGroup(
                    Item('add_parameter_button',
                         springy=True,
                         enabled_when='object.parameter_entity_creator'
                                      '.model is not None'),
                    Item('remove_parameter_button',
                         enabled_when='selected_parameter is not None'),
                    show_labels=False,
                ),
            )
        )

        return traits_view

    # -------------------
    #      Defaults
    # -------------------

    def _parameter_entity_creator_default(self):
        """Returns an entity creator containing parameter types
        from all installed plugins"""

        if self.model is not None:
            visible_factories = [
                f for f in self.model.factory.parameter_factories
                if f.ui_visible
            ]

            parameter_entity_creator = NewEntityCreator(
                factories=visible_factories,
                dclick_function=self._dclick_add_parameter,
                factory_name='MCO Parameter',
                config_visible=False
            )
            return parameter_entity_creator

    def _parameter_model_views_default(self):
        """Creates a list of MCOParameterModelViews for each
        model.parameter"""
        parameter_model_views = []

        if self.model is not None:
            # Add all MCO parameters as ModelViews
            parameter_model_views += [
                MCOParameterModelView(model=parameter)
                for parameter in self.model.parameters
            ]

        return parameter_model_views

    def _selected_parameter_default(self):
        """Default value for selected_kpi"""
        if len(self.parameter_model_views) > 0:
            return self.parameter_model_views[0]

    # -------------------
    #     Listeners
    # -------------------

    @on_trait_change('model')
    def update_parameter_entity_creator(self):
        """ Update the entity creator based on the MCO factory """
        self.parameter_entity_creator = (
                self._parameter_entity_creator_default()
        )

    # Update parameter_model_views when model changes
    @on_trait_change('model.parameters')
    def update_parameter_model_views(self):
        """ Update the MCOParameterModelView(s) """
        self.parameter_model_views = self._parameter_model_views_default()

        # Update the selected_parameter view
        if len(self.parameter_model_views) == 0:
            self.selected_parameter = None

    # Workflow Validation
    @on_trait_change('parameter_model_views.verify_workflow_event')
    def received_verify_request(self):
        """Pass on request for verify_workflow_event"""
        self.verify_workflow_event = True

    def _add_parameter_button_fired(self):
        """Call add_parameter to create a new empty parameter using
        the parameter_entity_creator"""
        self.add_parameter(self.parameter_entity_creator.model)
        self.parameter_entity_creator.reset_model()

        self.selected_parameter = self.parameter_model_views[-1]

    def _remove_parameter_button_fired(self):
        """Call remove_parameter to delete selected_parameter"""

        index = self.parameter_model_views.index(self.selected_parameter)
        self.remove_parameter(self.selected_parameter.model)

        # Update user selection
        if len(self.parameter_model_views) > 0:
            if index == 0:
                self.selected_parameter = self.parameter_model_views[index]
            else:
                self.selected_parameter = self.parameter_model_views[index-1]

    # -------------------
    #   Private Methods
    # -------------------

    def _dclick_add_parameter(self, ui_info):
        """Called when a parameter factory is double clicked in the entity
        creator. The ui_info object is automatically passed by the
        parameter_entity_creator and is unused
        """
        self._add_parameter_button_fired()

    # -------------------
    #    Public Methods
    # -------------------

    def add_parameter(self, parameter):
        """Adds a parameter to the MCO model associated with this view.

        Parameters
        ----------
        parameter: BaseMCOParameter
            The parameter to be added to the current MCO.
        """
        self.model.parameters.append(parameter)

    def remove_parameter(self, parameter):
        """Removes a parameter from the MCO model associated with this
        view.

        Parameters
        ----------
        parameter: BaseMCOParameter
            The parameter to be removed from the current MCO.
        """
        self.model.parameters.remove(parameter)
        self.verify_workflow_event = True
