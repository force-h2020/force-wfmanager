#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

from traits.api import (
    Instance, Str, on_trait_change, Property,
    cached_property, List, Button, Tuple
)
from traitsui.api import (
    View, Item, HGroup, ListEditor, VGroup, InstanceEditor
)

from force_bdss.api import Identifier
from force_bdss.local_traits import CUBAType

from force_wfmanager.ui.setup.mco.base_mco_options_view import \
    BaseMCOOptionsView
from force_wfmanager.ui.setup.mco.mco_parameter_model_view import \
    MCOParameterModelView
from force_wfmanager.ui.setup.new_entity_creator import NewEntityCreator


class MCOParameterView(BaseMCOOptionsView):

    # -------------------
    # Regular Attributes
    # -------------------

    #: The human readable name of the MCOParameterView class
    name = Str('Parameters')

    # --------------------
    # Dependent Attributes
    # --------------------

    #: Creates new instances of MCO Parameters
    parameter_entity_creator = Instance(NewEntityCreator)

    # ----------
    # Properties
    # ----------

    #: A list of variable names and types, each from a variable
    #: that could become a MCO parameter
    parameter_name_options = Property(
        List(Tuple(Identifier, CUBAType)),
        depends_on='variable_names_registry.data_source_inputs'
    )

    # ------------------
    #      Buttons
    # ------------------

    #: Button to add a new parameter to the MCO using the
    #: parameter_entity_creator
    add_parameter_button = Button('New Parameter')

    #: Button to remove selected_model_view from the MCO
    remove_parameter_button = Button('Delete Parameter')

    def default_traits_view(self):
        """Creates a traits view containing a notebook list of existing MCO
        parameters above an entity creator from which the user can select new
        parameter types"""

        # Defines a list editor to display model_views
        parameter_editor = ListEditor(
            page_name='.label',
            use_notebook=True,
            dock_style='tab',
            selected='selected_model_view')

        traits_view = View(
            VGroup(
                #: Displays existing parameters
                VGroup(
                    Item('model_views',
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
                         enabled_when='selected_model_view is not None'),
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

    def _model_views_default(self):
        """Creates a list of MCOParameterModelViews for each
        model.parameter"""
        model_views = []

        if self.model is not None:
            # Add all MCO parameters as ModelViews
            model_views += [
                MCOParameterModelView(
                    model=parameter,
                    available_variables=self.parameter_name_options
                )
                for parameter in self.model.parameters
            ]

        return model_views

    # -------------------
    #     Listeners
    # -------------------

    @cached_property
    def _get_parameter_name_options(self):
        """Listens to variable_names_registry to extract
         possible names for new MCO parameters"""
        parameter_name_options = []
        if self.variable_names_registry is not None:
            outputs = self.variable_names_registry.data_source_outputs
            inputs = self.variable_names_registry.data_source_inputs
            parameter_name_options += (
                [input_ for input_ in inputs
                 if input_ not in outputs]
            )

        return parameter_name_options

    @on_trait_change('model')
    def update_parameter_entity_creator(self):
        """ Update the entity creator based on the MCO factory """
        self.parameter_entity_creator = (
                self._parameter_entity_creator_default()
        )

    # Update model_views when model.parameters changes
    @on_trait_change('model.parameters')
    def update_parameter_model_views(self):
        """ Triggers the base method update_model_views when
        MCOParameters are updated"""
        self.update_model_views()

    # Workflow Validation
    @on_trait_change('parameter_name_options')
    def update_model_views__combobox(self):
        """Update the parameter model view name options"""
        for parameter_view in self.model_views:
            parameter_view.available_variables = self.parameter_name_options

    def _add_parameter_button_fired(self):
        """Call add_parameter to create a new empty parameter using
        the parameter_entity_creator"""
        self.add_parameter(self.parameter_entity_creator.model)
        self.parameter_entity_creator.reset_model()

        # Highlight new Parameter in ListEditor
        self.selected_model_view = self.model_views[-1]

    def _remove_parameter_button_fired(self):
        """Call remove_parameter to delete selected parameter from model"""
        self._remove_button_action(self.remove_parameter)

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
