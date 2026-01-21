from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal


class EntityMergerView(QtWidgets.QDialog):
    """Dialog for resolving merge conflicts when creating entities from multiple bases."""

    # Signals
    equation_selected = pyqtSignal(object)  # Emitted when an equation is selected
    undo_requested = pyqtSignal()  # Emitted when undo is requested

    def __init__(self, merger_data, parent=None):
        """Initialize the merger view.
        
        Args:
            merger_data: Dictionary containing the merger state
            parent: Parent widget
        """
        super().__init__(parent)

        self.merger_data = merger_data
        self.setup_ui()
        self.setup_connections()

        # Set window properties
        self.setWindowTitle("Resolve Merge Conflicts")
        self.setMinimumSize(600, 400)

    def setup_ui(self):
        """Set up the user interface."""
        layout = QtWidgets.QVBoxLayout(self)

        # Title
        title = QtWidgets.QLabel("Resolve Merge Conflicts")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)

        # Variable info
        self.variable_label = QtWidgets.QLabel()
        self.variable_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.variable_label)

        # Equation list
        self.equations_list = QtWidgets.QListView()
        self.equations_list.setModel(self.merger_data['equations_model'])
        self.equations_list.setItemDelegate(
                QtWidgets.QStyledItemDelegate()
                )
        layout.addWidget(self.equations_list)

        # Button box
        button_box = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.Ok |
                QtWidgets.QDialogButtonBox.Cancel
                )

        # Undo button
        self.undo_button = QtWidgets.QPushButton("Undo")
        self.undo_button.setEnabled(False)
        button_box.addButton(
                self.undo_button,
                QtWidgets.QDialogButtonBox.ActionRole
                )

        layout.addWidget(button_box)

        # Connect standard buttons
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    def setup_connections(self):
        """Set up signal connections."""
        self.equations_list.doubleClicked.connect(
                lambda: self.equation_selected.emit(
                        self.equations_list.currentIndex()
                        )
                )
        self.undo_button.clicked.connect(self.undo_requested.emit)

    def update_view(self, var_id, equations_model):
        """Update the view with new conflict data.
        
        Args:
            var_id: ID of the variable with conflicts
            equations_model: Model containing the conflicting equations
        """
        self.variable_label.setText(f"Select equation for variable: {var_id}")
        self.equations_list.setModel(equations_model)

    def set_undo_enabled(self, enabled):
        """Enable or disable the undo button.
        
        Args:
            enabled: Whether to enable the undo button
        """
        self.undo_button.setEnabled(enabled)

    def showEvent(self, event):
        """Handle show event."""
        super().showEvent(event)
        self.show_event_triggered.emit()
