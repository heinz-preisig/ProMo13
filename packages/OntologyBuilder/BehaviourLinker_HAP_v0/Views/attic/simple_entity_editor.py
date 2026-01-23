# from PyQt5 import QtCore, QtWidgets, QtGui
# from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidgetItem, QStyledItemDelegate
# from PyQt5.QtCore import Qt
# from OntologyBuilder.BehaviourLinker_HAP_v0.Models import image_list
# from OntologyBuilder.BehaviourLinker_HAP_v0.Delegates.image_list import ImageItemDelegate
#
#
# class SimpleEntityEditor(QtWidgets.QDialog):
#     """Simplified entity editor that combines view and controller logic."""
#
#     def __init__(self, entity, all_variables, all_equations, parent=None):
#         super().__init__(parent)
#         self.entity = entity
#         self.all_variables = all_variables or {}  # Ensure this is never None
#         self.all_equations = all_equations or {}  # Ensure this is never None
#
#         # Debug info
#         print(f"\n=== SimpleEntityEditor Initialization ===")
#         print(f"Entity: {getattr(entity, 'entity_name', 'Unknown')}")
#         print(f"Number of variables: {len(self.all_variables)}")
#         print(f"Number of equations: {len(self.all_equations)}")
#         if self.all_variables:
#             print("First few variables:")
#             for i, (var_id, var) in enumerate(list(self.all_variables.items())[:3]):
#                 print(f"  {i + 1}. {var_id} (type: {type(var)})")
#         print("=" * 40 + "\n")
#
#         self.setup_ui()
#         self.setup_connections()
#         self.load_data()
#
#     def setup_ui(self):
#         self.setWindowTitle(f"Edit Entity: {getattr(self.entity, 'entity_name', 'Untitled')}")
#         self.setMinimumSize(800, 600)
#
#         # Main layout
#         layout = QtWidgets.QVBoxLayout(self)
#
#         # Variables section
#         var_group = QtWidgets.QGroupBox("Variables")
#         var_layout = QtWidgets.QVBoxLayout()
#
#         # Variable list
#         self.var_list = QtWidgets.QListView()
#         self.var_model = image_list.ImageListModel()
#         self.var_list.setModel(self.var_model)
#         self.var_list.setItemDelegate(ImageItemDelegate(self.var_list))
#         var_layout.addWidget(self.var_list)
#
#         # Variable buttons
#         btn_layout = QtWidgets.QHBoxLayout()
#         self.add_btn = QtWidgets.QPushButton("Add Variable")
#         self.edit_btn = QtWidgets.QPushButton("Edit")
#         self.delete_btn = QtWidgets.QPushButton("Delete")
#
#         btn_layout.addWidget(self.add_btn)
#         btn_layout.addWidget(self.edit_btn)
#         btn_layout.addWidget(self.delete_btn)
#         var_layout.addLayout(btn_layout)
#
#         var_group.setLayout(var_layout)
#         layout.addWidget(var_group)
#
#         # Equations section
#         eq_group = QtWidgets.QGroupBox("Equations")
#         eq_layout = QtWidgets.QVBoxLayout()
#
#         self.eq_list = QtWidgets.QListView()
#         self.eq_model = image_list.ImageListModel()
#         self.eq_list.setModel(self.eq_model)
#         self.eq_list.setItemDelegate(ImageItemDelegate(self.eq_list))
#         eq_layout.addWidget(self.eq_list)
#
#         eq_group.setLayout(eq_layout)
#         layout.addWidget(eq_group)
#
#         # Dialog buttons
#         btn_box = QtWidgets.QDialogButtonBox(
#             QtWidgets.QDialogButtonBox.Ok |
#             QtWidgets.QDialogButtonBox.Cancel
#         )
#         btn_box.accepted.connect(self.accept)
#         btn_box.rejected.connect(self.reject)
#         layout.addWidget(btn_box)
#
#     def setup_connections(self):
#         self.add_btn.clicked.connect(self.on_add_variable)
#         self.edit_btn.clicked.connect(self.on_edit_variable)
#         self.delete_btn.clicked.connect(self.on_delete_variable)
#         self.var_list.selectionModel().currentChanged.connect(
#             self.on_selection_changed
#         )
#
#     def load_data(self):
#         """Load entity data into the UI."""
#         try:
#             # Debug: Print current state before loading
#             print("\n=== Loading Data ===")
#             print(f"Entity variables: {getattr(self.entity, 'variables', {})}")
#             print(f"Entity equations: {getattr(self.entity, 'equations', {})}")
#             print(f"Entity var_eq_forest: {getattr(self.entity, 'var_eq_forest', [])}")
#
#             # Get variable and equation IDs from the entity
#             var_ids = self.entity.get_variables() if hasattr(self.entity, 'get_variables') else []
#             eq_ids = self.entity.get_equations() if hasattr(self.entity, 'get_equations') else []
#
#             print(f"Variables from get_variables(): {var_ids}")
#             print(f"Equations from get_equations(): {eq_ids}")
#
#             # Also check if there are variables in the entity's variables dictionary
#             if hasattr(self.entity, 'variables') and isinstance(self.entity.variables, dict):
#                 for var_id in self.entity.variables.keys():
#                     if var_id not in var_ids and var_id in self.all_variables:
#                         print(f"Adding variable from entity.variables: {var_id}")
#                         var_ids.append(var_id)
#
#             # Load variables
#             variables = []
#             for var_id in var_ids:
#                 if var_id in self.all_variables:
#                     variables.append(self.all_variables[var_id])
#                 else:
#                     print(f"Warning: Variable {var_id} not found in all_variables")
#
#             print(f"After processing, total variables to display: {len(variables)}")
#
#             # Load equations
#             equations = []
#             for eq_id in eq_ids:
#                 if eq_id in self.all_equations:
#                     equations.append(self.all_equations[eq_id])
#                 else:
#                     print(f"Warning: Equation {eq_id} not found in all_equations")
#
#             print(f"Loaded {len(variables)} variables and {len(equations)} equations")
#
#             # Block signals to prevent unnecessary updates
#             self.var_list.blockSignals(True)
#             self.eq_list.blockSignals(True)
#
#             try:
#                 # Clear existing data with model reset
#                 self.var_model.beginResetModel()
#                 self.eq_model.beginResetModel()
#
#                 # Load new data
#                 self.var_model.load_data(variables)
#                 self.eq_model.load_data(equations)
#
#                 # Update the views
#                 self.var_model.endResetModel()
#                 self.eq_model.endResetModel()
#
#                 # Force update the views
#                 self.var_list.viewport().update()
#                 self.eq_list.viewport().update()
#
#                 # Ensure the views are properly updated
#                 self.var_list.update()
#                 self.eq_list.update()
#
#                 # Force a repaint of the entire widget
#                 self.var_list.repaint()
#                 self.eq_list.repaint()
#
#                 print("UI updated successfully")
#
#             except Exception as e:
#                 print(f"Error updating models: {str(e)}")
#                 import traceback
#                 traceback.print_exc()
#                 self.var_model.endResetModel()
#                 self.eq_model.endResetModel()
#
#             finally:
#                 # Always unblock signals when done
#                 self.var_list.blockSignals(False)
#                 self.eq_list.blockSignals(False)
#
#         except Exception as e:
#             print(f"Error in load_data: {str(e)}")
#             import traceback
#             traceback.print_exc()
#
#         # Force an immediate update of the UI
#         QtCore.QCoreApplication.processEvents()
#
#     def on_add_variable(self):
#         """Handle adding a new variable to the entity using the complex variable editor."""
#         from OntologyBuilder.BehaviourLinker_HAP_v0.Views.variable_selection import VariableSelectionView
#         from OntologyBuilder.BehaviourLinker_HAP_v0.Models.variable_editor import VariableEditorModel
#         from OntologyBuilder.BehaviourLinker_HAP_v0.Views.variable_editor import VariableEditorView
#         from OntologyBuilder.BehaviourLinker_HAP_v0.Controllers.variable_editor import VariableEditorController
#
#         print("\n=== DEBUG: on_add_variable ===")
#         print(f"Total variables in all_variables: {len(self.all_variables) if hasattr(self, 'all_variables') else 'N/A'}")
#
#         # Get unused variables
#         if not hasattr(self, 'all_variables') or not hasattr(self.entity, 'get_variables'):
#             print("Error: Missing required attributes")
#             return
#
#         # Get the list of unused variables
#         unused_vars = []
#         try:
#             used_vars = set(self.entity.get_variables())
#             unused_vars = []
#             for var_id, var in self.all_variables.items():
#                 if var_id not in used_vars:
#                     # Ensure each variable has the required methods
#                     if not hasattr(var, 'get_id'):
#                         var.get_id = lambda v=var_id: v
#                     if not hasattr(var, 'get_img_path'):
#                         var.get_img_path = lambda v=var_id: f"{v}.png"
#                     unused_vars.append(var)
#             print(f"Found {len(unused_vars)} unused variables")
#         except Exception as e:
#             print(f"Error getting unused variables: {e}")
#             import traceback
#             traceback.print_exc()
#             return
#
#         if not unused_vars:
#             QtWidgets.QMessageBox.information(
#                 self,
#                 "No Variables Available",
#                 "All available variables are already added to this entity."
#             )
#             return
#
#         # Show variable selection dialog
#         dlg = VariableSelectionView(unused_vars, self)
#         if dlg.exec_() == QtWidgets.QDialog.Accepted:
#             selected_var = dlg.get_selected_variable()
#             if selected_var:
#                 try:
#                     # Create the variable editor model
#                     var_editor_model = VariableEditorModel(
#                         self.entity,
#                         selected_var,
#                         self.all_variables,
#                         self.all_equations
#                     )
#
#                     # Create and show the variable editor
#                     var_editor_view = VariableEditorView(var_editor_model, False, self)
#                     var_editor_controller = VariableEditorController(var_editor_model, var_editor_view)
#
#                     if var_editor_view.exec_() == QtWidgets.QDialog.Accepted:
#                         # The controller should handle updating the model
#                         # Just refresh our view
#                         self.load_data()
#                         return True
#
#                 except Exception as e:
#                     print(f"Error in variable editor: {e}")
#                     import traceback
#                     traceback.print_exc()
#                     QtWidgets.QMessageBox.critical(
#                         self,
#                         "Error",
#                         f"Failed to edit variable: {str(e)}"
#                     )
#                     # Force a complete refresh of the UI
#                     self.load_data()
#
#                     # Explicitly update the models
#                     self.var_model.layoutAboutToBeChanged.emit()
#                     self.var_model.layoutChanged.emit()
#                     self.eq_model.layoutAboutToBeChanged.emit()
#                     self.eq_model.layoutChanged.emit()
#
#                     # Force a repaint of the views
#                     self.var_list.viewport().update()
#                     self.eq_list.viewport().update()
#
#     def on_edit_variable(self):
#         """Edit the selected variable."""
#         index = self.var_list.currentIndex()
#         if not index.isValid():
#             return
#
#         var_id = index.data()
#         self._edit_variable(var_id)
#
#     def on_delete_variable(self):
#         """Delete the selected variable from the entity."""
#         index = self.var_list.currentIndex()
#         if not index.isValid():
#             return
#
#         var_id = index.data()
#
#         # Confirm deletion
#         reply = QtWidgets.QMessageBox.question(
#             self,
#             'Confirm Deletion',
#             f'Are you sure you want to remove variable "{var_id}" from this entity?',
#             QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
#         )
#
#         if reply == QtWidgets.QMessageBox.Yes:
#             self.entity.remove_variable(var_id)
#             self.load_data()  # Refresh the view
#
#     def on_selection_changed(self, current, previous):
#         """Enable/disable edit/delete buttons based on selection."""
#         has_selection = current.isValid()
#         self.edit_btn.setEnabled(has_selection)
#         self.delete_btn.setEnabled(has_selection)
#
#     def _edit_variable(self, var_id):
#         """Edit a variable using a simplified dialog."""
#         if var_id not in self.all_variables:
#             return
#
#         from OntologyBuilder.BehaviourLinker_HAP_v0.Views.simple_variable_editor import SimpleVariableEditor
#
#         var = self.all_variables[var_id]
#         dlg = SimpleVariableEditor(
#             variable=var,
#             all_equations=self.all_equations,
#             parent=self
#         )
#
#         if dlg.exec_() == QtWidgets.QDialog.Accepted:
#             # The dialog handles saving changes directly to the variable
#             self.load_data()  # Refresh the view
#
#     def get_entity(self):
#         """Return the edited entity."""
#         return self.entity
