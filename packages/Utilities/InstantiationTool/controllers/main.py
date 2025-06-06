from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot

from packages.Common.classes import io

# from packages.OntologyBuilder.BehaviourLinker.Delegates.image_list import ImageItemDelegate
from packages.dialogs.views import list_selector
from packages.OntologyBuilder.BehaviourLinker.Delegates.image_list import (
    ImageItemDelegate,
)
from packages.Utilities.InstantiationTool.delegates.topology_tree_item import (
    CustomTopologyItemDelegate,
)
from packages.Utilities.InstantiationTool.models.main import MainModel
from packages.Utilities.InstantiationTool.views.main import MainView
from src.common.components import image_list


class MainController(QObject):
    def __init__(self, main_model: MainModel, main_view: MainView) -> None:
        super().__init__()

        self._model = main_model
        self._view = main_view

        # self._view.ui.tree_required_variables.setModel(
        #     self._model.variable_tree_model)

        var_list_controller = image_list.ImageListController(
            self._view.ui.tree_required_variables, self._model.variable_list
        )
        self._view.ui.tree_topology_objects.setModel(self._model.topology_tree_model)
        delegate = CustomTopologyItemDelegate(self._view.ui.tree_topology_objects)
        self._view.ui.tree_topology_objects.setItemDelegate(delegate)
        self._view.set_topology_tree_settings()

        # Connections from the View
        self._view.show_event_triggered.connect(self.select_ontology)
        self._view.ui.tree_required_variables.clicked.connect(
            self._model.on_variables_selected
        )

        self._view.ui.pbutton_instantiate.clicked.connect(self.on_instantiate_clicked)

        self._view.ui.action_save.triggered.connect(self._model.save_instantiation)

        # Connections from the Model
        self._model.topology_tree_changed.connect(self._view.on_topology_tree_changed)
        self._model.selection_changed.connect(self._view.on_selection_changed)
        self._model.topology_tree_model.check_box_state_changed.connect(
            self._model.on_topology_tree_model_check_box_changed
        )

    def select_ontology(self) -> None:
        """Launches a Dialog to get the ontology name.

        If the Dialog gets accepted it calls the
        """
        dlg = list_selector.ListSelectorView(
            io.get_available_ontologies(),
            self._view,
            "Ontology selection",
            "Select an ontology:",
        )

        model_selected = False
        while not model_selected:
            dialog_status = dlg.exec_()
            if dialog_status == QtWidgets.QDialog.Rejected:
                self.load_default_data()
                break

            ontology_name = dlg.ui.list.currentIndex().data()
            model_selected = self.select_model(ontology_name)

    def select_model(self, ontology_name: str) -> bool:
        dlg = list_selector.ListSelectorView(
            io.get_available_models(ontology_name),
            self._view,
            "Model selection",
            "Select a model:",
        )

        dialog_status = dlg.exec_()
        if dialog_status == QtWidgets.QDialog.Rejected:
            return False

        model_name = dlg.ui.list.currentIndex().data()
        self._model.load_ontology_info(ontology_name, model_name)

        return True

    def on_instantiate_clicked(self) -> None:
        # TODO: Catch this exception with a suitable notification system.
        instantiation_value = self._view.ui.ledit_instantiate.text()
        try:
            float(instantiation_value)
        except ValueError:
            instantiation_value = None

        var_index = self._view.ui.tree_required_variables.currentIndex()

        if instantiation_value is not None:
            self._model.instantiate(instantiation_value, var_index)

        self._view.ui.ledit_instantiate.setText("")
