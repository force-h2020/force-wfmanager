from traits.api import (HasStrictTraits, Instance, List, Button,
                        on_trait_change, Dict)
from traitsui.api import (View, Handler, HSplit, VGroup, UItem,
                          HGroup, ListStrEditor)

from force_bdss.api import BaseKPICalculatorModel, BaseKPICalculatorBundle
from force_bdss.workspecs.workflow import Workflow

from .view_utils import ListAdapter


class ModalHandler(Handler):
    def object_add_kpi_calculator_button_changed(self, info):
        if info.object.current_model is not None:
            info.object.workflow.kpi_calculators.append(
                info.object.current_model
            )
        info.ui.dispose(True)

    def object_cancel_button_changed(self, info):
        info.ui.dispose(False)


class NewKPICalculatorModal(HasStrictTraits):
    """ Dialog which allows the user to add a new KPICalculator to the workflow
    """
    workflow = Instance(Workflow)

    #: Available kpi calculator bundles
    available_kpi_calculators = List(BaseKPICalculatorBundle)

    #: Selected kpi calculator bundle in the list of kpi calculators
    selected_kpi_calculator = Instance(BaseKPICalculatorBundle)

    add_kpi_calculator_button = Button("Add")
    cancel_button = Button('Cancel')

    _models = Dict()

    current_model = Instance(BaseKPICalculatorModel)

    traits_view = View(
        VGroup(
            HSplit(
                UItem(
                    "available_kpi_calculators",
                    editor=ListStrEditor(
                        adapter=ListAdapter(),
                        selected="selected_kpi_calculator"),
                ),
                UItem('current_model', style='custom')
            ),
            HGroup(
                UItem('add_kpi_calculator_button'),
                UItem('cancel_button')
            )
        ),
        title='New KPI Calculator',
        handler=ModalHandler(),
        width=800,
        height=600,
        kind="livemodal"
    )

    @on_trait_change("selected_kpi_calculator")
    def update_current_model(self):
        selected_kpi_calculator_id = id(self.selected_kpi_calculator)
        if self._models.get(selected_kpi_calculator_id) is None:
            model = self.selected_kpi_calculator.create_model()
            self._models[selected_kpi_calculator_id] = model
            self.current_model = model
        else:
            self.current_model = self._models.get(selected_kpi_calculator_id)
