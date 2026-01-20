from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from OntologyBuilder.BehaviourLinker_HAP_v0.Views.Compiled_UIs import entity_merger_ui


class EntityMergerView(QtWidgets.QDialog):
  show_event_triggered = QtCore.pyqtSignal()

  def __init__(self, model, parent=None):
    super().__init__(parent)

    # Set up the user interface
    self.ui = entity_merger_ui.Ui_entity_merger()
    self.ui.setupUi(self)

    self._model = model

    self.ui.pbutton_previous.setEnabled(False)
    self.ui.label_variable.setText("")

  def load_label_img(self, path):
    pixmap = QtGui.QPixmap(path)
    self.ui.label_variable.setPixmap(pixmap)

  def set_pbutton_previous_state(self, is_previous_allowed):
    self.ui.pbutton_previous.setEnabled(is_previous_allowed)
