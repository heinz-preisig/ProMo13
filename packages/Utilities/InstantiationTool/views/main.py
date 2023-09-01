from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from packages.Utilities.InstantiationTool.views.Compiled_UIs import main_ui
from packages.Utilities.InstantiationTool.models.main import MainModel


class MainView(QtWidgets.QMainWindow):
  show_event_triggered = QtCore.pyqtSignal()

  def __init__(self, main_model: MainModel):
    super().__init__()

    # Set up the user interface from Designer
    self.ui = main_ui.Ui_MainWindow()
    self.ui.setupUi(self)

    self._model = main_model

    # self.ui.tree_topology_objects.setHeader()

    # header().setHorizontalHeaderLabels(["Name", "Value"])

    # self.ui.menuEntity.setFocus()
    # self.ui.actionEdit.setEnabled(False)
    # self.ui.actionDelete.setEnabled(False)

  def showEvent(self, event) -> None:
    super().showEvent(event)
    self.show_event_triggered.emit()

  def on_variable_tree_changed(self):
    self.ui.tree_required_variables.expandAll()
    # self.ui.tree_entities.clearSelection()
    self.ui.tree_required_variables.setCurrentIndex(QtCore.QModelIndex())

  def set_topology_tree_settings(self):
    self.ui.tree_topology_objects.setHeaderHidden(False)
    self.ui.tree_topology_objects.header().setDefaultAlignment(QtCore.Qt.AlignCenter)
    self.ui.tree_topology_objects.header().setStretchLastSection(False)
    self.ui.tree_topology_objects.setColumnWidth(1, 80)

    self.ui.tree_topology_objects.header().setSectionResizeMode(
        0, QtWidgets.QHeaderView.Stretch)

  def on_topology_tree_changed(self):
    self.ui.tree_topology_objects.expandAll()
    # self.ui.tree_entities.clearSelection()
    self.ui.tree_topology_objects.setCurrentIndex(QtCore.QModelIndex())

  # def menu_items_state(self, index: QtCore.QModelIndex):
  #   print("hello")
  #   self.ui.actionEdit.setEnabled(index.isValid())
  #   self.ui.actionDelete.setEnabled(index.isValid())
