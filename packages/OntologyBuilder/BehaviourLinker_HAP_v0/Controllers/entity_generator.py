from typing import List

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QListView

from OntologyBuilder.BehaviourLinker_HAP_v0.Models.entity_generator import EntityGeneratorModel
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.entity_generator import EntityGeneratorView
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.insert_str import InsertStrView


# TODO List
# 1. Animations for the list.
# 2. Fix animations skip when next/prev buttons are pressed fast.
# 3. Probably change so Arc/Node is first in the entity name.


class EntityGeneratorController(QtCore.QObject):
  def __init__(self, model: EntityGeneratorModel, view: EntityGeneratorView):
    super().__init__()

    self._model = model
    self._view = view

    self.stacked_views: List[QListView] = [
            None,
            self._view.ui.list_network,
            self._view.ui.list_token,
            self._view.ui.list_mechanism,
            self._view.ui.list_nature,
            ]

    for i in range(1, 5):
      self.stacked_views[i].setModel(self._model.stacked_models[i])

    self._view.ui.tree_bases.setModel(self._model.tree_bases_model)

    # Connecting signal -> slots
    # Signals from the View
    self._view.ui.pbutton_next.clicked.connect(self.on_next_button_clicked)
    self._view.ui.pbutton_previous.clicked.connect(
            self.on_previous_button_clicked)
    self._view.ui.pbutton_cancel.clicked.connect(self._view.reject)
    self._view.ui.pbutton_finish.clicked.connect(
            self.on_finish_button_clicked)
    for i in range(1, 5):
      self.stacked_views[i].selectionModel().selectionChanged.connect(
              self.on_list_selection_change)
      self.stacked_views[i].doubleClicked.connect(self.on_next_button_clicked)

    # Signals from the Model
    self._model.tree_changed.connect(self._view.on_tree_changed)

  def on_next_button_clicked(self):
    current_page = self._view.ui.stackedWidget.currentIndex()

    new_value = None
    if current_page == 0:
      if self._view.ui.rbutton_node.isChecked():
        new_value = "node"
      else:
        new_value = "arc"
    else:
      new_value = self.stacked_views[current_page].selectedIndexes()

    self._model.update_summary(current_page, new_value)
    self._model.update_stacked_models(current_page + 1)

    self._view.next_page()

  def on_previous_button_clicked(self):
    self._view.previous_page()
    self.on_list_selection_change()

  def on_finish_button_clicked(self):
    # Update the summary model with the selected bases.
    new_value = self._view.ui.tree_bases.selectedIndexes()
    current_page = self._view.ui.stackedWidget.currentIndex()
    self._model.update_summary(current_page, new_value)

    used_names = self._model.get_used_names()
    forbidden_names = [name.lower() for name in used_names]

    dlg = InsertStrView(
            "Entity name",
            "Insert a name for the new entity:",
            forbidden_names,
            self._view
            )
    result = dlg.exec_()
    if result == QtWidgets.QDialog.Accepted:
      self._model.add_entity_name(dlg.ui.ledit_input.text())
      self._view.accept()

  def on_list_selection_change(self):
    current_page = self._view.ui.stackedWidget.currentIndex()
    if current_page != 0:
      selection = self.stacked_views[current_page].selectedIndexes()

    self._view.ui.pbutton_next.setEnabled(bool(selection))
