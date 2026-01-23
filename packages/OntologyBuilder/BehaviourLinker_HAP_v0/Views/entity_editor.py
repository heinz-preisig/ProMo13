# In OntologyBuilder/BehaviourLinker_HAP_v0/Views/entity_editor.py

from typing import Optional
from PyQt5 import QtWidgets, QtCore
from OntologyBuilder.BehaviourLinker_HAP_v0.Views.Compiled_UIs import entity_editor_ui
from OntologyBuilder.BehaviourLinker_HAP_v0.Models.entity_editor import EntityEditorModel


class EntityEditorView(QtWidgets.QDialog):
    # Signal emitted when the dialog is shown
    show_event_triggered = QtCore.pyqtSignal()
    
    def __init__(
            self,
            model: EntityEditorModel,
            parent: Optional[QtWidgets.QWidget] = None,
            is_variant: bool = False,
            variant_source_name: str = ""
    ):
        super().__init__(parent)
        # Rest of the __init__ method...

        # Set up the user interface
        self.ui = entity_editor_ui.Ui_entity_editor()
        self.ui.setupUi(self)

        self._model = model
        self.is_variant = is_variant

        # Update window title and UI based on creation mode
        if is_variant and variant_source_name:
            self.setWindowTitle(f"Create Variant of: {variant_source_name}")
            # Add variant-specific UI elements if needed
        else:
            self.setWindowTitle("Create New Instance")

        # Rest of the initialization...
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
