from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from packages.OntologyBuilder.BehaviourLinker_HAP_v0.Views.Compiled_UIs import main_ui
from packages.OntologyBuilder.BehaviourLinker_HAP_v0.Models.main import MainModel


class MainView(QtWidgets.QMainWindow):
  show_event_triggered = QtCore.pyqtSignal()

  def __init__(self, main_model: MainModel):
    super().__init__()

    # Set up the user interface from Designer
    self.ui = main_ui.Ui_MainWindow()
    self.ui.setupUi(self)

    self._model = main_model

  def showEvent(self, event) -> None:
    super().showEvent(event)
    self.show_event_triggered.emit()

  # def on_tree_changed(self):
  #   self.ui.tree_entities.expandAll()
  #   # self.ui.tree_entities.clearSelection()
  #   self.ui.tree_entities.setCurrentIndex(QtCore.QModelIndex())

  # def menu_items_state(self, index: QtCore.QModelIndex):
  #   print("hello")
  #   self.ui.actionEdit.setEnabled(index.isValid())
  #   self.ui.actionDelete.setEnabled(index.isValid())
