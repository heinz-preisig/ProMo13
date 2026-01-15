from typing import List

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import QStringListModel, QItemSelection, QItemSelectionModel
from PyQt5.QtWidgets import QAbstractItemView, QListView

from OntologyBuilder.BehaviourLinker.Models.entity_editor import EntityEditorModel
from OntologyBuilder.BehaviourLinker.Views.entity_editor import EntityEditorView
from OntologyBuilder.BehaviourLinker.Delegates import image_list


from OntologyBuilder.BehaviourLinker.Views.variable_editor import VariableEditorView
from OntologyBuilder.BehaviourLinker.Controllers.variable_editor import VariableEditorController

from OntologyBuilder.BehaviourLinker.Views.entity_changes import EntityChangesView
from OntologyBuilder.BehaviourLinker.Views.variable_selection import VariableSelectionView

# TODO List
# 1. Filter the list of available variables to add.
# 2. Automatically mark as input or instantiation some variables.


class EntityEditorController(QtCore.QObject):
  selectionStatusChanged = QtCore.pyqtSignal(bool)

  def __init__(self, model: EntityEditorModel, view: EntityEditorView):
    super().__init__()

    self._model = model
    self._view = view

    self._view.ui.list_variables.setModel(self._model.variables_model)
    delegate = image_list.IconImageItemDelegate(self._view.ui.list_variables)
    self._view.ui.list_variables.setItemDelegate(delegate)

    self._view.ui.list_equations.setModel(self._model.equations_model)
    delegate = image_list.ImageItemDelegate(self._view.ui.list_equations)
    self._view.ui.list_equations.setItemDelegate(delegate)

    # Connecting signals to slots
    # View signals
    self._view.ui.pbutton_accept.clicked.connect(self._view.accept)
    self._view.ui.pbutton_cancel.clicked.connect(self._view.reject)
    self._view.ui.cbox_view_all.stateChanged.connect(
        lambda state:  self._model.on_view_all_changed(
            state == QtCore.Qt.Checked)
    )

    self._view.ui.list_variables.selectionModel().currentChanged.connect(
        self.on_current_changed
    )

    self._view.ui.pbutton_add_variable.clicked.connect(self.on_add_var_clicked)
    self._view.ui.pbutton_delete_variable.clicked.connect(
        self.on_delete_var_clicked)

    self._view.ui.list_variables.doubleClicked.connect(self.edit_variable)
    self._view.ui.pbutton_edit_variable.clicked.connect(
        lambda: self.edit_variable(self._view.ui.list_variables.currentIndex()))

    # Model signals
    self._model.variableChecked.connect(self._view.update_delete_button)

    # Controller signals
    self.selectionStatusChanged.connect(self._view.update_edit_button)
    self.selectionStatusChanged.connect(self._view.update_delete_button)

  def edit_variable(self, index, output_only=False):
    dlg_model = self._model.get_variable_editor_model(index)
    dlg_view = VariableEditorView(dlg_model, output_only, self._view)
    dlg_controller = VariableEditorController(dlg_model, dlg_view)

    result = dlg_view.exec_()
    if result == QtWidgets.QDialog.Accepted:
      self._model.update_variables_model()
      self._model.update_equations_model()

  def on_add_var_clicked(self):
    variable_list = self._model.get_unused_variables()
    dlg_view = VariableSelectionView(variable_list, self._view)
    result = dlg_view.exec_()
    if result == QtWidgets.QDialog.Rejected:
      return

    var_id = dlg_view.ui.list_variables.currentIndex().data()
    index = self._model.add_new_output_var(var_id)

    self.selectionStatusChanged.emit(False)

    self.edit_variable(index, True)

  def on_delete_var_clicked(self):
    index = self._view.ui.list_variables.currentIndex()

    changes = self._model.changes_from_delete_var(index)
    dlg = EntityChangesView(changes, self._view)

    result = dlg.exec_()
    if result == QtWidgets.QDialog.Rejected:
      return

    self._model.accept_changes(index)
    self.selectionStatusChanged.emit(False)

  def on_current_changed(self, index):
    self.selectionStatusChanged.emit(index.isValid())

    if index.isValid():
      self._model.check_variable(index)
