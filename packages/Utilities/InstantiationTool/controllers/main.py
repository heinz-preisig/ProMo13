import sys

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
from src.common.components import image_list, starting_dialog


class MainController(QObject):
    def __init__(self, main_model: MainModel, main_view: MainView) -> None:
        super().__init__()

        self._model = main_model
        self._view = main_view
        self._model._view = self._view

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
        # In MainController.__init__
        self._model.update_instantiate_field.connect(self._view.ui.ledit_instantiate.setText)

    def select_ontology(self) -> None:
        """Launches a Dialog to get the ontology name.

        If the Dialog gets accepted it calls the
        """
        available_ontologies = self._model.get_available_ontologies()
        view = starting_dialog.StartingDialogView()
        controller = starting_dialog.StartingDialogController(
            view, available_ontologies
        )

        model_selected = False
        while not model_selected:
            result = view.exec_()
            if result == QtWidgets.QDialog.Accepted:
                ontology_name = view.ui.selection_list.currentIndex().data()
                model_selected = self.select_model(ontology_name)
            else:
                sys.exit()

    def select_model(self, ontology_name: str) -> bool:
        available_models = self._model.get_available_models(ontology_name)
        view = starting_dialog.StartingDialogView()
        controller = starting_dialog.StartingDialogController(view, available_models)

        result = view.exec_()
        if result == QtWidgets.QDialog.Accepted:
            model_name = view.ui.selection_list.currentIndex().data()
            self._model.load_ontology_info(ontology_name, model_name)
            return True

        return False

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

        # self._view.ui.ledit_instantiate.setText("")
