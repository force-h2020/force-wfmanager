from traits.api import (
    Instance, Unicode, Bool, on_trait_change, Event, Property
)
from traitsui.api import View, Item, ModelView, Group

from force_bdss.api import BaseMCOParameter

from force_wfmanager.ui.ui_utils import get_factory_name


class MCOParameterModelView(ModelView):

    # -------------------
    # Required Attributes
    # -------------------

    #: MCO parameter model
    model = Instance(BaseMCOParameter, allow_none=False)

    # ------------------
    # Dependent Attributes
    # ------------------

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

    # ----------
    # Properties
    # ----------

    #: The human readable name of the MCO parameter class
    label = Property(Unicode(), depends_on="model.[name,type]")

    # ----
    # View
    # ----

    def default_traits_view(self):

        content = [Item('model.name'),
                   Item('model.type')]

        parameter_view = self.model.trait_view()

        for group in parameter_view.content.content:
            for item in group.content:
                content.append(
                    Item(f'model.{item.name}')
                )

        traits_view = View(
                Group(content),
                kind='subpanel'
            )

        return traits_view

    # Workflow Validation

    @on_trait_change('model.[name,type]')
    def parameter_change(self):
        self.verify_workflow_event = True

    # Properties

    def _get_label(self):
        if self.model.name == '' and self.model.type == '':
            return self._label_default()
        return self._label_default()+': {type} {name}'.format(
            type=self.model.type, name=self.model.name
        )

    # Defaults

    def _label_default(self):
        return get_factory_name(self.model.factory)
