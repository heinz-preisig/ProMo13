from PyQt5 import QtCore
from PyQt5 import QtWidgets

from OntologyBuilder.BehaviourLinker_HAP_v0.Views.Compiled_UIs import entity_editor_ui


class EntityEditorView(QtWidgets.QDialog):
  show_event_triggered = QtCore.pyqtSignal()

  def __init__(self, model, parent=None):
    super().__init__(parent)

    # Set up the user interface
    self.ui = entity_editor_ui.Ui_entity_editor()
    self.ui.setupUi(self)

    self._model = model
    
    # Set window title with just the friendly name (part after last dot)
    if hasattr(model, 'editing_entity') and hasattr(model.editing_entity, 'entity_name'):
        friendly_name = model.editing_entity.entity_name.split('.')[-1]
        self.setWindowTitle(f"Edit: {friendly_name}")

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
