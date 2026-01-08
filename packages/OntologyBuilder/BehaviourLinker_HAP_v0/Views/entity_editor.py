from typing import List

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import QStringListModel, QItemSelection, QItemSelectionModel
from PyQt5.QtWidgets import QAbstractItemView, QListView

from packages.Common.classes import ontology
from packages.OntologyBuilder.BehaviourLinker.Views.Compiled_UIs import entity_editor_ui


class EntityEditorView(QtWidgets.QDialog):
  show_event_triggered = QtCore.pyqtSignal()

  def __init__(self, model, parent=None):
    super().__init__(parent)

    # Set up the user interface
    self.ui = entity_editor_ui.Ui_entity_editor()
    self.ui.setupUi(self)

    self._model = model

    self.ui.cbox_view_all.setChecked(True)
    self.ui.pbutton_delete_variable.setEnabled(False)
    self.ui.pbutton_edit_variable.setEnabled(False)

  def update_delete_button(self, is_enabled: bool):
    self.ui.pbutton_delete_variable.setEnabled(is_enabled)

  def update_edit_button(self, is_enabled: bool):
    self.ui.pbutton_edit_variable.setEnabled(is_enabled)

  def showEvent(self, event) -> None:
    super().showEvent(event)
    self.show_event_triggered.emit()
