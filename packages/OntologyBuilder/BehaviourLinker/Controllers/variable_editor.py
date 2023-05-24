from typing import List

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import QStringListModel, QItemSelection, QItemSelectionModel
from PyQt5.QtWidgets import QAbstractItemView, QListView

from packages.OntologyBuilder.BehaviourLinker.Models.variable_editor import VariableEditorModel
from packages.OntologyBuilder.BehaviourLinker.Views.variable_editor import VariableEditorView
from packages.OntologyBuilder.BehaviourLinker.Delegates import image_list
from packages.OntologyBuilder.BehaviourLinker.Views.entity_changes import EntityChangesView
# TODO List


class VariableEditorController(QtCore.QObject):
  input_checked = QtCore.pyqtSignal(QtCore.QModelIndex)
  output_checked = QtCore.pyqtSignal()
  init_checked = QtCore.pyqtSignal(QtCore.QModelIndex)
  equation_selected = QtCore.pyqtSignal()

  def __init__(self, model: VariableEditorModel, view: VariableEditorView):
    super().__init__()

    self._model = model
    self._view = view

    self._view.ui.list_equations.setModel(self._model.equations_model)
    delegate = image_list.ImageItemDelegate(self._view.ui.list_equations)
    self._view.ui.list_equations.setItemDelegate(delegate)

    # Signals from the view
    self._view.ui.pbutton_accept.clicked.connect(self.on_accept_clicked)
    self._view.ui.pbutton_cancel.clicked.connect(self._view.reject)

    self._view.ui.cbox_input.stateChanged.connect(self.on_input_state_changed)
    self._view.ui.cbox_output.stateChanged.connect(
        self.on_output_state_changed)
    self._view.ui.cbox_instantiation.stateChanged.connect(
        self.on_init_state_changed)
    self._view.ui.list_equations.clicked.connect(
        self.on_equation_selected)

    self._view.ui.list_equations.clicked.connect(
        self.on_equation_selected)

    self._view.ui.list_equations.doubleClicked.connect(self.on_accept_clicked)
    # Signals from the controller
    self.input_checked.connect(self._view.on_input_checked)
    self.output_checked.connect(self._view.on_output_checked)
    self.init_checked.connect(self._view.on_init_checked)
    self.equation_selected.connect(self._view.on_equation_selected)
    # Signals from the model
    self._model.initial_data_fetched.connect(
        self._view.on_initial_data_fetched)

    self._model.fetch_initial_data()

  def on_input_state_changed(self, state):
    if state == QtCore.Qt.Checked:
      self.input_checked.emit(self._model.get_last_index())

  def on_output_state_changed(self, state):
    if state == QtCore.Qt.Checked:
      self.output_checked.emit()

  def on_init_state_changed(self, state):
    if state == QtCore.Qt.Checked:
      self.init_checked.emit(self._model.get_last_index())

  def on_equation_selected(self, index):
    if index != self._model.get_last_index():
      self.equation_selected.emit()

  def on_accept_clicked(self):
    final_config = {
        "is_input": self._view.ui.cbox_input.isChecked(),
        "is_output": self._view.ui.cbox_output.isChecked(),
        "is_init": self._view.ui.cbox_instantiation.isChecked(),
        "selected_eq": self._view.ui.list_equations.currentIndex()
    }
    print(final_config["selected_eq"].isValid())
    changes = self._model.compute_changes(final_config)

    if any(changes):
      dlg_view = EntityChangesView(changes, self._view)
      result = dlg_view.exec_()
      if result == QtWidgets.QDialog.Rejected:
        return

    self._model.accept_changes(final_config)
    self._view.accept()
