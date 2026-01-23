# from PyQt5 import QtCore, QtWidgets
# from OntologyBuilder.BehaviourLinker_HAP_v0.Models import image_list
# from OntologyBuilder.BehaviourLinker_HAP_v0.Delegates.image_list import ImageItemDelegate
#
#
# class SimpleVariableEditor(QtWidgets.QDialog):
#     """Simplified variable editor dialog."""
#
#     def __init__(self, variable, all_equations, parent=None):
#         super().__init__(parent)
#         self.variable = variable
#         self.all_equations = all_equations
#
#         self.setup_ui()
#         self.setup_connections()
#         self.load_data()
#
#     def setup_ui(self):
#         self.setWindowTitle(f"Edit Variable: {getattr(self.variable, 'var_id', 'Untitled')}")
#         self.setMinimumSize(600, 400)
#
#         # Main layout
#         layout = QtWidgets.QVBoxLayout(self)
#
#         # Variable info
#         info_group = QtWidgets.QGroupBox("Variable Properties")
#         info_layout = QtWidgets.QFormLayout()
#
#         # ID (read-only)
#         self.id_label = QtWidgets.QLabel(getattr(self.variable, 'var_id', ''))
#         info_layout.addRow("ID:", self.id_label)
#
#         # Type (read-only)
#         self.type_label = QtWidgets.QLabel(getattr(self.variable, 'var_type', ''))
#         info_layout.addRow("Type:", self.type_label)
#
#         # Input/Output checkboxes
#         self.input_cb = QtWidgets.QCheckBox("Is Input")
#         self.output_cb = QtWidgets.QCheckBox("Is Output")
#         self.init_cb = QtWidgets.QCheckBox("Is Initialization")
#
#         info_layout.addRow(self.input_cb)
#         info_layout.addRow(self.output_cb)
#         info_layout.addRow(self.init_cb)
#
#         info_group.setLayout(info_layout)
#         layout.addWidget(info_group)
#
#         # Equations section
#         eq_group = QtWidgets.QGroupBox("Equations")
#         eq_layout = QtWidgets.QVBoxLayout()
#
#         self.eq_list = QtWidgets.QListView()
#         self.eq_model = image_list.ImageListModel()
#         self.eq_list.setModel(self.eq_model)
#         self.eq_list.setItemDelegate(ImageItemDelegate(self.eq_list))
#
#         eq_layout.addWidget(QtWidgets.QLabel("Select an equation:"))
#         eq_layout.addWidget(self.eq_list)
#         eq_group.setLayout(eq_layout)
#         layout.addWidget(eq_group)
#
#         # Dialog buttons
#         btn_box = QtWidgets.QDialogButtonBox(
#             QtWidgets.QDialogButtonBox.Ok |
#             QtWidgets.QDialogButtonBox.Cancel
#         )
#         btn_box.accepted.connect(self.on_accept)
#         btn_box.rejected.connect(self.reject)
#         layout.addWidget(btn_box)
#
#     def setup_connections(self):
#         self.eq_list.doubleClicked.connect(self.on_accept)
#
#     def load_data(self):
#         """Load variable data into the UI."""
#         # Set checkboxes
#         self.input_cb.setChecked(getattr(self.variable, 'is_input', False))
#         self.output_cb.setChecked(getattr(self.variable, 'is_output', False))
#         self.init_cb.setChecked(getattr(self.variable, 'is_initialization', False))
#
#         # Load equations
#         equations = [
#             eq for eq_id, eq in self.all_equations.items()
#             if hasattr(eq, 'is_applicable') and eq.is_applicable(self.variable.var_id)
#         ]
#         self.eq_model.load_data(equations)
#
#         # Select current equation if any
#         current_eq = getattr(self.variable, 'equation_id', None)
#         if current_eq and current_eq in self.all_equations:
#             for i, eq in enumerate(equations):
#                 if eq.eq_id == current_eq:
#                     self.eq_list.setCurrentIndex(self.eq_model.index(i, 0))
#                     break
#
#     def on_accept(self):
#         """Save changes and accept the dialog."""
#         # Update variable properties
#         self.variable.is_input = self.input_cb.isChecked()
#         self.variable.is_output = self.output_cb.isChecked()
#         self.variable.is_initialization = self.init_cb.isChecked()
#
#         # Update equation if one is selected
#         index = self.eq_list.currentIndex()
#         if index.isValid():
#             eq = self.eq_model.data(index, QtCore.Qt.UserRole)
#             if eq:
#                 self.variable.equation_id = eq.eq_id
#
#         self.accept()
#
#     def get_variable(self):
#         """Return the edited variable."""
#         return self.variable
