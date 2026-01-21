from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidgetItem, QStyledItemDelegate
from PyQt5.QtCore import Qt
from OntologyBuilder.BehaviourLinker_HAP_v0.Models import image_list
from OntologyBuilder.BehaviourLinker_HAP_v0.Delegates.image_list import ImageItemDelegate


class SimpleEntityEditor(QtWidgets.QDialog):
    """Simplified entity editor that combines view and controller logic."""
    
    def __init__(self, entity, all_variables, all_equations, parent=None):
        super().__init__(parent)
        self.entity = entity
        self.all_variables = all_variables
        self.all_equations = all_equations
        
        self.setup_ui()
        self.setup_connections()
        self.load_data()
        
    def setup_ui(self):
        self.setWindowTitle(f"Edit Entity: {getattr(self.entity, 'entity_name', 'Untitled')}")
        self.setMinimumSize(800, 600)
        
        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        
        # Variables section
        var_group = QtWidgets.QGroupBox("Variables")
        var_layout = QtWidgets.QVBoxLayout()
        
        # Variable list
        self.var_list = QtWidgets.QListView()
        self.var_model = image_list.ImageListModel()
        self.var_list.setModel(self.var_model)
        self.var_list.setItemDelegate(ImageItemDelegate(self.var_list))
        var_layout.addWidget(self.var_list)
        
        # Variable buttons
        btn_layout = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Add Variable")
        self.edit_btn = QtWidgets.QPushButton("Edit")
        self.delete_btn = QtWidgets.QPushButton("Delete")
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        var_layout.addLayout(btn_layout)
        
        var_group.setLayout(var_layout)
        layout.addWidget(var_group)
        
        # Equations section
        eq_group = QtWidgets.QGroupBox("Equations")
        eq_layout = QtWidgets.QVBoxLayout()
        
        self.eq_list = QtWidgets.QListView()
        self.eq_model = image_list.ImageListModel()
        self.eq_list.setModel(self.eq_model)
        self.eq_list.setItemDelegate(ImageItemDelegate(self.eq_list))
        eq_layout.addWidget(self.eq_list)
        
        eq_group.setLayout(eq_layout)
        layout.addWidget(eq_group)
        
        # Dialog buttons
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | 
            QtWidgets.QDialogButtonBox.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        
    def setup_connections(self):
        self.add_btn.clicked.connect(self.on_add_variable)
        self.edit_btn.clicked.connect(self.on_edit_variable)
        self.delete_btn.clicked.connect(self.on_delete_variable)
        self.var_list.selectionModel().currentChanged.connect(
            self.on_selection_changed
        )
        
    def load_data(self):
        """Load entity data into the UI."""
        try:
            # Debug: Print current state before loading
            print("\n=== Loading Data ===")
            print(f"Entity variables: {getattr(self.entity, 'variables', {})}")
            print(f"Entity equations: {getattr(self.entity, 'equations', {})}")
            print(f"Entity var_eq_forest: {getattr(self.entity, 'var_eq_forest', [])}")
            
            # Get variable and equation IDs from the entity
            var_ids = self.entity.get_variables() if hasattr(self.entity, 'get_variables') else []
            eq_ids = self.entity.get_equations() if hasattr(self.entity, 'get_equations') else []
            
            print(f"Variables from get_variables(): {var_ids}")
            print(f"Equations from get_equations(): {eq_ids}")
            
            # Also check if there are variables in the entity's variables dictionary
            if hasattr(self.entity, 'variables') and isinstance(self.entity.variables, dict):
                for var_id in self.entity.variables.keys():
                    if var_id not in var_ids and var_id in self.all_variables:
                        print(f"Adding variable from entity.variables: {var_id}")
                        var_ids.append(var_id)
            
            # Load variables
            variables = []
            for var_id in var_ids:
                if var_id in self.all_variables:
                    variables.append(self.all_variables[var_id])
                else:
                    print(f"Warning: Variable {var_id} not found in all_variables")
            
            print(f"After processing, total variables to display: {len(variables)}")
            
            # Load equations
            equations = []
            for eq_id in eq_ids:
                if eq_id in self.all_equations:
                    equations.append(self.all_equations[eq_id])
                else:
                    print(f"Warning: Equation {eq_id} not found in all_equations")
            
            print(f"Loaded {len(variables)} variables and {len(equations)} equations")
            
            # Block signals to prevent unnecessary updates
            self.var_list.blockSignals(True)
            self.eq_list.blockSignals(True)
            
            try:
                # Clear existing data with model reset
                self.var_model.beginResetModel()
                self.eq_model.beginResetModel()
                
                # Load new data
                self.var_model.load_data(variables)
                self.eq_model.load_data(equations)
                
                # Update the views
                self.var_model.endResetModel()
                self.eq_model.endResetModel()
                
                # Force update the views
                self.var_list.viewport().update()
                self.eq_list.viewport().update()
                
                # Ensure the views are properly updated
                self.var_list.update()
                self.eq_list.update()
                
                # Force a repaint of the entire widget
                self.var_list.repaint()
                self.eq_list.repaint()
                
                print("UI updated successfully")
                
            except Exception as e:
                print(f"Error updating models: {str(e)}")
                import traceback
                traceback.print_exc()
                self.var_model.endResetModel()
                self.eq_model.endResetModel()
                
            finally:
                # Always unblock signals when done
                self.var_list.blockSignals(False)
                self.eq_list.blockSignals(False)
                
        except Exception as e:
            print(f"Error in load_data: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Force an immediate update of the UI
        QtCore.QCoreApplication.processEvents()
        
    def on_add_variable(self):
        """Handle adding a new variable to the entity."""
        from OntologyBuilder.BehaviourLinker_HAP_v0.Views.variable_selection import VariableSelectionView
        import os
        
        # Debug: Print first equation structure if available
        if self.all_equations:
            first_eq_id = next(iter(self.all_equations))
            first_eq = self.all_equations[first_eq_id]
            print("\n=== DEBUG: First equation structure ===")
            print(f"Equation ID: {first_eq_id}")
            print(f"Equation object type: {type(first_eq)}")
            print(f"Equation attributes: {dir(first_eq)}")
            if hasattr(first_eq, 'lhs'):
                print(f"LHS type: {type(first_eq.lhs)}")
                print(f"LHS content: {first_eq.lhs}")
            if hasattr(first_eq, 'get_id'):
                print(f"Equation ID via get_id(): {first_eq.get_id()}")
            if hasattr(first_eq, 'img_path'):
                print(f"Image path: {first_eq.img_path}")
            print("=" * 40 + "\n")
        
        # Get unused variables
        unused_vars = [
            var for var_id, var in self.all_variables.items()
            if var_id not in self.entity.get_variables()
        ]
        
        if not unused_vars:
            QtWidgets.QMessageBox.information(
                self,
                "No Variables Available",
                "All available variables are already added to this entity."
            )
            return
            
        # Show variable selection dialog
        dlg = VariableSelectionView(unused_vars, self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            selected_var = dlg.get_selected_variable()
            if selected_var:
                # Get the variable ID from the selected variable object
                if hasattr(selected_var, 'get_id'):
                    var_id = selected_var.get_id()
                else:
                    var_id = str(selected_var)
                
                # Extract just the variable ID from the path if it's a path
                if var_id.endswith('.png'):
                    var_id = os.path.splitext(os.path.basename(var_id))[0]
                print(f"Selected variable ID: {var_id}")
                print(f"Looking for equations with LHS variable: {var_id}")
                
                # Show equation selection dialog
                eq_dialog = QtWidgets.QDialog(self)
                eq_dialog.setWindowTitle("Select Equation")
                layout = QtWidgets.QVBoxLayout()
                
                # Add label with variable ID (not path)
                var_name = var_id.split('/')[-1].replace('.png', '')  # Extract just the variable name
                label = QtWidgets.QLabel(f"Select an equation for variable: {var_name}")
                layout.addWidget(label)
                
                # Create a custom delegate for rendering equation items
                # In the on_add_variable method, around line 165-250, the structure should be:

                # Create a custom delegate for rendering equation items
                class EquationDelegate(QtWidgets.QStyledItemDelegate):
                    def __init__(self, parent=None):
                        super().__init__(parent)
                        self.pixmap_cache = {}

                    def sizeHint(self, option, index):
                        # Reduced height to 40px, width to 400px
                        return QtCore.QSize(400, 40)

                    def paint(self, painter, option, index):
                        # Get the item data
                        eq_id = index.data(Qt.UserRole)
                        img_path = index.data(Qt.UserRole + 1)

                        # Configure the painter
                        painter.save()
                        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

                        # Draw selection background
                        if option.state & QtWidgets.QStyle.State_Selected:
                            painter.fillRect(option.rect, option.palette.highlight())

                        # Draw image if available
                        if img_path and QtCore.QFile.exists(img_path):
                            if img_path not in self.pixmap_cache:
                                pixmap = QtGui.QPixmap(img_path)
                                if not pixmap.isNull():
                                    # Scale to fit within item height while maintaining aspect ratio
                                    target_height = option.rect.height() - 4  # 2px padding top and bottom
                                    scaled_width = int(pixmap.width() * (target_height / pixmap.height()))
                                    pixmap = pixmap.scaled(
                                            scaled_width, target_height,
                                            Qt.KeepAspectRatio,
                                            Qt.SmoothTransformation
                                            )
                                    self.pixmap_cache[img_path] = pixmap

                            if img_path in self.pixmap_cache:
                                pixmap = self.pixmap_cache[img_path]
                                # Center the image both horizontally and vertically
                                x_offset = (option.rect.width() - pixmap.width()) // 2
                                y_offset = (option.rect.height() - pixmap.height()) // 2
                                painter.drawPixmap(
                                        option.rect.x() + x_offset,
                                        option.rect.y() + y_offset,
                                        pixmap
                                        )

                        painter.restore()

                # Create list widget with custom delegate
                eq_list = QtWidgets.QListWidget()
                eq_list.setItemDelegate(EquationDelegate(eq_list))
                eq_list.setViewMode(QtWidgets.QListView.ListMode)
                eq_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
                eq_list.setSpacing(2)  # Reduced spacing between items
                eq_list.setStyleSheet("""
                                    QListWidget {
                                        border: 1px solid #d0d0d0;
                                        border-radius: 3px;
                                        padding: 1px;
                                        background: white;
                                        outline: none;
                                    }
                                    QListWidget::item {
                                        border: 1px solid #e0e0e0;
                                        border-radius: 2px;
                                        margin: 1px 0;
                                        background: white;
                                    }
                                    QListWidget::item:selected {
                                        background: #3a7bd5;
                                        border: 1px solid #2c5fb3;
                                    }
                                    QListWidget::item:hover {
                                        background: #f0f7ff;
                                        border: 1px solid #cce0ff;
                                    }
                                """)
                
                # Add equations where the variable is on LHS
                equations_found = False
                for eq_id, eq in self.all_equations.items():
                    # Check if the equation has a left-hand side
                    if not hasattr(eq, 'lhs') or not eq.lhs:
                        continue
                        
                    # Get the LHS variable ID
                    lhs_var_id = None
                    if isinstance(eq.lhs, dict) and 'global_ID' in eq.lhs:
                        lhs_var_id = eq.lhs['global_ID']
                    
                    # Check if this equation is for our variable
                    var_in_lhs = (lhs_var_id == var_id)
                    
                    # Debug output for first few equations
                    if eq_id in list(self.all_equations.keys())[:3]:  # Only show first 3 for brevity
                        print(f"Checking equation {eq_id}: LHS var={lhs_var_id}, looking for {var_id}, match={var_in_lhs}")
                        
                    if not var_in_lhs:
                        continue
                        
                    equations_found = True
                    img_path = getattr(eq, 'img_path', '')
                    eq_text = getattr(eq, 'text', eq_id)
                    
                    try:
                        if img_path and QtCore.QFile.exists(img_path):
                            # Create pixmap from equation image
                            pixmap = QtGui.QPixmap(img_path)
                            if not pixmap.isNull():
                                # Scale pixmap if needed
                                pixmap = pixmap.scaled(200, 50, 
                                                    Qt.KeepAspectRatio, 
                                                    Qt.SmoothTransformation)
                                
                                # Create item with text and store image path in UserRole+1
                                item = QtWidgets.QListWidgetItem(eq_text)
                                item.setData(Qt.UserRole, eq_id)  # Store the ID as user data
                                item.setData(Qt.UserRole + 1, img_path)  # Store img_path for the delegate
                                item.setToolTip(f"Equation ID: {eq_id}")
                                eq_list.addItem(item)
                                continue
                        
                        # Fallback to text if image loading fails or not available
                        item = QtWidgets.QListWidgetItem(eq_text)
                        item.setData(Qt.UserRole, eq_id)
                        item.setToolTip(f"Equation ID: {eq_id}")
                        eq_list.addItem(item)
                        
                    except Exception as e:
                        print(f"Error loading image {img_path}: {e}")
                        # Fallback to text if image loading fails
                        item = QtWidgets.QListWidgetItem(eq_text)
                        item.setData(Qt.UserRole, eq_id)
                        item.setToolTip(f"Equation ID: {eq_id}")
                        eq_list.addItem(item)
                
                if not equations_found:
                    msg = f"No equations found where {var_id} is on the left-hand side."
                    print(msg)
                    layout.addWidget(QtWidgets.QLabel(msg))
                    
                    # Debug: Show available LHS variables from equations
                    debug_vars = set()
                    for eq in self.all_equations.values():
                        if hasattr(eq, 'lhs') and eq.lhs and isinstance(eq.lhs, dict) and 'global_ID' in eq.lhs:
                            debug_vars.add(eq.lhs['global_ID'])
                    if debug_vars:
                        print(f"Available LHS variables in equations: {sorted(debug_vars)}")
                    else:
                        print("No equations with valid LHS found in the system.")
                else:
                    layout.addWidget(eq_list)
                
                # Add OK/Cancel buttons
                buttons = QtWidgets.QDialogButtonBox(
                    QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
                )
                buttons.accepted.connect(eq_dialog.accept)
                buttons.rejected.connect(eq_dialog.reject)
                layout.addWidget(buttons)
                
                eq_dialog.setLayout(layout)
                
                if eq_dialog.exec_() == QtWidgets.QDialog.Accepted and equations_found:
                    selected_items = eq_list.selectedItems()
                    if selected_items:
                        # Get the selected equation ID from user data
                        eq_id = selected_items[0].data(Qt.UserRole)
                        print(f"Selected equation: {eq_id}")
                        
                        try:
                            # Ensure the variable is in the entity's variables
                            if not hasattr(self.entity, 'variables'):
                                self.entity.variables = {}
                            
                            # Add the variable if it doesn't exist
                            if not hasattr(self.entity, 'variables') or not isinstance(self.entity.variables, dict):
                                self.entity.variables = {}
                            
                            # Add the variable to the entity's variables dictionary
                            if var_id not in self.entity.variables:
                                self.entity.variables[var_id] = self.all_variables.get(var_id, {})
                                print(f"Added {var_id} to entity.variables")
                            else:
                                print(f"Variable {var_id} already in entity.variables")
                            
                            # Initialize var_eq_forest if it doesn't exist
                            if not hasattr(self.entity, 'var_eq_forest'):
                                self.entity.var_eq_forest = []
                            
                            # Check if variable already exists in any tree in the forest
                            var_in_forest = any(var_id in tree for tree in self.entity.var_eq_forest)
                            
                            if var_in_forest:
                                # Variable exists, update its equation
                                for tree in self.entity.var_eq_forest:
                                    if var_id in tree:
                                        # Update the equation for this variable
                                        tree[var_id] = [eq_id]
                                        # Add equation to the tree if not present
                                        if eq_id not in tree:
                                            tree[eq_id] = []
                                        break
                            else:
                                # Variable doesn't exist, add a new tree for it
                                print(f"Adding new variable {var_id} with equation {eq_id}")
                                new_tree = {var_id: [eq_id], eq_id: []}
                                self.entity.var_eq_forest.append(new_tree)
                            
                            # Ensure the equation is in the entity's equations
                            if not hasattr(self.entity, 'equations'):
                                self.entity.equations = {}
                            if eq_id not in self.entity.equations and eq_id in self.all_equations:
                                self.entity.equations[eq_id] = self.all_equations[eq_id]
                                
                            # Update the variable in the entity's variables
                            if not hasattr(self.entity, 'variables'):
                                self.entity.variables = {}
                            if var_id not in self.entity.variables and var_id in self.all_variables:
                                self.entity.variables[var_id] = self.all_variables[var_id]
                            
                            # Debug: Print current state before refresh
                            print("\n=== Before UI Refresh ===")
                            print(f"Entity variables: {getattr(self.entity, 'variables', {})}")
                            print(f"Entity equations: {getattr(self.entity, 'equations', {})}")
                            print(f"Entity var_eq_forest: {getattr(self.entity, 'var_eq_forest', [])}")
                            
                            # Force a complete refresh of the UI
                            self.load_data()
                            
                            # Debug: Verify the variable was added
                            current_vars = self.entity.get_variables() if hasattr(self.entity, 'get_variables') else []
                            current_eqs = self.entity.get_equations() if hasattr(self.entity, 'get_equations') else []
                            
                            print("\n=== After UI Refresh ===")
                            print(f"Entity variables: {getattr(self.entity, 'variables', {})}")
                            print(f"Entity equations: {getattr(self.entity, 'equations', {})}")
                            print(f"Entity var_eq_forest: {getattr(self.entity, 'var_eq_forest', [])}")
                            print(f"Current variables: {current_vars}")
                            print(f"Current equations: {current_eqs}")
                            
                            if var_id in current_vars:
                                print(f"Successfully added variable {var_id} with equation {eq_id}")
                            else:
                                print(f"Warning: Variable {var_id} not found in entity after adding")
                                
                        except Exception as e:
                            print(f"Error adding variable: {str(e)}")
                            import traceback
                            traceback.print_exc()
                            
                            # Fallback: Try to add variable directly to the entity
                            try:
                                if not hasattr(self.entity, 'variables'):
                                    self.entity.variables = {}
                                self.entity.variables[var_id] = self.all_variables.get(var_id, {})
                                
                                if not hasattr(self.entity, 'equations'):
                                    self.entity.equations = {}
                                if eq_id in self.all_equations:
                                    self.entity.equations[eq_id] = self.all_equations[eq_id]
                                
                                if not hasattr(self.entity, 'var_eq_forest'):
                                    self.entity.var_eq_forest = []
                                
                                # Add a new tree for this variable
                                new_tree = {var_id: [eq_id], eq_id: []}
                                self.entity.var_eq_forest.append(new_tree)
                                
                                print(f"Added {var_id} directly to entity (fallback)")
                                
                                # Force a complete refresh of the UI
                                self.load_data()
                                
                                # Explicitly update the models
                                self.var_model.layoutAboutToBeChanged.emit()
                                self.var_model.layoutChanged.emit()
                                self.eq_model.layoutAboutToBeChanged.emit()
                                self.eq_model.layoutChanged.emit()
                                
                                # Force a repaint of the views
                                self.var_list.viewport().update()
                                self.eq_list.viewport().update()
                                
                            except Exception as e2:
                                print(f"Fallback also failed: {str(e2)}")
                
    def on_edit_variable(self):
        """Edit the selected variable."""
        index = self.var_list.currentIndex()
        if not index.isValid():
            return
            
        var_id = index.data()
        self._edit_variable(var_id)
        
    def on_delete_variable(self):
        """Delete the selected variable from the entity."""
        index = self.var_list.currentIndex()
        if not index.isValid():
            return
            
        var_id = index.data()
        
        # Confirm deletion
        reply = QtWidgets.QMessageBox.question(
            self,
            'Confirm Deletion',
            f'Are you sure you want to remove variable "{var_id}" from this entity?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.entity.remove_variable(var_id)
            self.load_data()  # Refresh the view
            
    def on_selection_changed(self, current, previous):
        """Enable/disable edit/delete buttons based on selection."""
        has_selection = current.isValid()
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        
    def _edit_variable(self, var_id):
        """Edit a variable using a simplified dialog."""
        if var_id not in self.all_variables:
            return
            
        from OntologyBuilder.BehaviourLinker_HAP_v0.Views.simple_variable_editor import SimpleVariableEditor
        
        var = self.all_variables[var_id]
        dlg = SimpleVariableEditor(
            variable=var,
            all_equations=self.all_equations,
            parent=self
        )
        
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            # The dialog handles saving changes directly to the variable
            self.load_data()  # Refresh the view

    def get_entity(self):
        """Return the edited entity."""
        return self.entity
