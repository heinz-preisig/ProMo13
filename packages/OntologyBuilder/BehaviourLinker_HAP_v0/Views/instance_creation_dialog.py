# In OntologyBuilder/BehaviourLinker_HAP_v0/Views/instance_creation_dialog.py

from typing import Optional, Tuple, Any
from PyQt5 import QtWidgets, QtCore
from Common.classes.entity import Entity


class InstanceCreationDialog(QtWidgets.QDialog):
    def __init__(
            self,
            parent: Optional[QtWidgets.QWidget] = None,
            existing_instances: Optional[list[Entity]] = None
            ):
        super().__init__(parent)
        # Rest of the __init__ method...

    def get_selection(self) -> Tuple[bool, Optional[Entity]]:
        """Get the user's selection.

        Returns:
            tuple: (is_variant, selected_instance)
        """
        is_variant = self.variant_radio.isChecked()
        if is_variant:
            index = self.instance_combo.currentIndex()
            if index >= 0:
                return is_variant, self.instance_combo.itemData(index)
        return is_variant, None
        self.setWindowTitle("Create New Instance")
        self.setMinimumWidth(400)

        layout = QtWidgets.QVBoxLayout(self)

        # Radio buttons for creation type
        self.type_group = QtWidgets.QButtonGroup(self)

        # New instance option
        self.new_instance_radio = QtWidgets.QRadioButton("Create New Instance")
        self.new_instance_radio.setChecked(True)
        self.type_group.addButton(self.new_instance_radio)

        # Variant option
        self.variant_radio = QtWidgets.QRadioButton("Create Variant of Existing")
        self.type_group.addButton(self.variant_radio)

        # Combo box for selecting source instance (only enabled for variant)
        self.instance_combo = QtWidgets.QComboBox()
        self.instance_combo.setEnabled(False)

        # Populate with existing instances
        self.existing_instances = existing_instances or []
        for instance in self.existing_instances:
            self.instance_combo.addItem(instance.entity_name, instance)

        # Connect signals
        self.variant_radio.toggled.connect(self.instance_combo.setEnabled)

        # Buttons
        button_box = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
                )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Add widgets to layout
        layout.addWidget(QtWidgets.QLabel("Select creation type:"))
        layout.addWidget(self.new_instance_radio)
        layout.addWidget(self.variant_radio)
        layout.addWidget(self.instance_combo)
        layout.addWidget(button_box)

    def get_selection(self):
        """Get the user's selection.

        Returns:
            tuple: (is_variant, selected_instance)
        """
        is_variant = self.variant_radio.isChecked()
        if is_variant:
            index = self.instance_combo.currentIndex()
            if index >= 0:
                return is_variant, self.instance_combo.itemData(index)
        return is_variant, None