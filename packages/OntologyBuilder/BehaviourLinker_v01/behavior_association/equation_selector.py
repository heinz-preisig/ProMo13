#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
Equation Selector Dialog for CAM12/ProMo
===============================================================================

This module provides a dialog for selecting equations that define variables,
with support for multiple equations and initialization options.
"""

import os
import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from Common.pop_up_message_box import makeMessageBox


class EquationSelectorDialog(QtWidgets.QDialog):
    """
    Dialog for selecting equations that define a selected variable.
    Supports multiple equations and initialization options.
    """
    
    def __init__(self, variable_data, ontology_container, parent=None):
        super().__init__(parent)
        
        self.variable_data = variable_data
        self.ontology_container = ontology_container
        self.selected_equation = None
        self.initialization_value = None
        self.use_initialization = False
        
        self.setup_ui()
        self.load_equations()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Select Equation for Variable Definition")
        self.setGeometry(200, 200, 600, 500)
        self.setModal(True)
        
        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        
        # Variable info
        var_label = self.variable_data.get('label', 'Unknown Variable')
        var_id = self.variable_data.get('id', 'Unknown ID')
        
        info_group = QtWidgets.QGroupBox("Selected Variable")
        info_layout = QtWidgets.QVBoxLayout(info_group)
        
        var_info = QtWidgets.QLabel(f"Variable: {var_label} (ID: {var_id})")
        var_info.setStyleSheet("font-weight: bold; font-size: 12px;")
        info_layout.addWidget(var_info)
        
        layout.addWidget(info_group)
        
        # Definition method selection
        method_group = QtWidgets.QGroupBox("Definition Method")
        method_layout = QtWidgets.QVBoxLayout(method_group)
        
        self.method_radio_group = QtWidgets.QButtonGroup()
        
        self.equation_radio = QtWidgets.QRadioButton("Define by Equation")
        self.equation_radio.setChecked(True)
        self.equation_radio.toggled.connect(self.on_method_changed)
        method_layout.addWidget(self.equation_radio)
        
        self.initialization_radio = QtWidgets.QRadioButton("Initialize with Value")
        self.initialization_radio.toggled.connect(self.on_method_changed)
        method_layout.addWidget(self.initialization_radio)
        
        self.method_radio_group.addButton(self.equation_radio, 0)
        self.method_radio_group.addButton(self.initialization_radio, 1)
        
        layout.addWidget(method_group)
        
        # Equation selection area
        self.equation_group = QtWidgets.QGroupBox("Select Equation")
        equation_layout = QtWidgets.QVBoxLayout(self.equation_group)
        
        # Equation list with enhanced display
        self.equation_list = QtWidgets.QListWidget()
        self.equation_list.setIconSize(QtCore.QSize(200, 50))  # Smaller size for equation images
        self.equation_list.setSpacing(5)
        self.equation_list.setUniformItemSizes(True)
        self.equation_list.setViewMode(QtWidgets.QListWidget.ListMode)  # List mode for text + icon
        self.equation_list.itemSelectionChanged.connect(self.on_equation_selection_changed)
        # Set item size to ensure proper layout
        self.equation_list.setMinimumHeight(200)
        equation_layout.addWidget(self.equation_list)
        
        # Equation details
        self.equation_details = QtWidgets.QLabel("Select an equation to see details")
        self.equation_details.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc; }")
        self.equation_details.setWordWrap(True)
        equation_layout.addWidget(self.equation_details)
        
        layout.addWidget(self.equation_group)
        
        # Initialization area
        self.initialization_group = QtWidgets.QGroupBox("Initialization Value")
        init_layout = QtWidgets.QVBoxLayout(self.initialization_group)
        
        self.init_value_input = QtWidgets.QLineEdit()
        self.init_value_input.setPlaceholderText("Enter numerical value or expression")
        init_layout.addWidget(self.init_value_input)
        
        # Add common initialization options
        common_frame = QtWidgets.QFrame()
        common_layout = QtWidgets.QHBoxLayout(common_frame)
        
        common_layout.addWidget(QtWidgets.QLabel("Common:"))
        
        zero_btn = QtWidgets.QPushButton("0")
        zero_btn.clicked.connect(lambda: self.init_value_input.setText("0"))
        common_layout.addWidget(zero_btn)
        
        one_btn = QtWidgets.QPushButton("1")
        one_btn.clicked.connect(lambda: self.init_value_input.setText("1"))
        common_layout.addWidget(one_btn)
        
        neg_one_btn = QtWidgets.QPushButton("-1")
        neg_one_btn.clicked.connect(lambda: self.init_value_input.setText("-1"))
        common_layout.addWidget(neg_one_btn)
        
        common_layout.addStretch()
        init_layout.addWidget(common_frame)
        
        layout.addWidget(self.initialization_group)
        
        # Initially hide initialization group
        self.initialization_group.setVisible(False)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.ok_button = QtWidgets.QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_selection)
        self.ok_button.setEnabled(False)
        
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def load_equations(self):
        """Load available equations for the selected variable from the ontology container"""
        try:
            self.equation_list.clear()
            
            # Get equations from variable data first (to get the list of equation IDs)
            variable_equations = self.variable_data.get('equations', {})
            print(f"Debug: Variable ID: {self.variable_data.get('id', 'Unknown')}")
            print(f"Debug: Variable label: {self.variable_data.get('label', 'Unknown')}")
            print(f"Debug: Variable network: {self.variable_data.get('network', 'Unknown')}")
            print(f"Debug: Variable equations: {list(variable_equations.keys())}")
            print(f"Debug: Number of equations: {len(variable_equations)}")
            
            if not variable_equations:
                # No equations available
                item = QtWidgets.QListWidgetItem("No equations available for this variable")
                item.setData(QtCore.Qt.UserRole, None)
                self.equation_list.addItem(item)
                self.equation_radio.setEnabled(False)
                self.initialization_radio.setChecked(True)
                self.on_method_changed()
                return
            
            # Get full equation data from ontology container's equation dictionary
            equation_dictionary = getattr(self.ontology_container, 'equation_dictionary', {})
            print(f"Debug: Equation dictionary has {len(equation_dictionary)} equations")
            
            # Add each equation to the list
            for eq_id in variable_equations:
                print(f"Debug: Processing equation {eq_id}")
                
                # Get equation data from ontology container (has PNG file info)
                eq_data = equation_dictionary.get(eq_id, {})
                
                # Fall back to variable data if not found in dictionary
                if not eq_data:
                    eq_data = variable_equations[eq_id]
                    print(f"Debug: Using variable data fallback for {eq_id}")
                else:
                    print(f"Debug: Found {eq_id} in equation dictionary")
                
                eq_label = eq_data.get('label', f'Equation_{eq_id}')
                eq_expression = eq_data.get('expression', 'No expression')
                # Try to get latex expression from variable data if not in equation dictionary
                if 'expression' not in eq_data and 'rhs' in variable_equations[eq_id]:
                    rhs_data = variable_equations[eq_id]['rhs']
                    eq_expression = rhs_data.get('latex', 'No expression')
                
                png_file = eq_data.get('png_file')
                
                print(f"Debug: {eq_id} -> Label: {eq_label}, Expression: {eq_expression}, PNG: {png_file}")
                
                # Create list item - show label only when PNG is available, otherwise show LaTeX text
                if png_file and os.path.exists(png_file):
                    item_text = eq_label  # Only show label, PNG will show the equation
                else:
                    item_text = f"{eq_label}\n{eq_expression}"  # Show LaTeX text when no PNG
                
                item = QtWidgets.QListWidgetItem(item_text)
                item.setData(QtCore.Qt.UserRole, eq_id)
                
                # Add LaTeX PNG image if available
                if png_file and os.path.exists(png_file):
                    try:
                        # Method 1: Try loading as QPixmap first
                        pixmap = QtGui.QPixmap(png_file)
                        if not pixmap.isNull():
                            # Scale pixmap to fit icon size
                            scaled_pixmap = pixmap.scaled(200, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                            icon = QtGui.QIcon(scaled_pixmap)
                            if not icon.isNull():
                                item.setIcon(icon)
                                print(f"✓ Loaded PNG icon for {eq_id}: {png_file} ({pixmap.width()}x{pixmap.height()})")
                            else:
                                print(f"⚠ PNG icon is null for {eq_id}: {png_file}")
                        else:
                            print(f"⚠ PNG pixmap is null for {eq_id}: {png_file}")
                            
                            # Method 2: Try direct QIcon loading as fallback
                            icon_direct = QtGui.QIcon(png_file)
                            if not icon_direct.isNull():
                                item.setIcon(icon_direct)
                                print(f"✓ Loaded PNG icon (direct) for {eq_id}: {png_file}")
                            else:
                                print(f"⚠ Direct PNG icon also null for {eq_id}: {png_file}")
                                
                    except Exception as e:
                        print(f"✗ Error loading PNG icon for {eq_id}: {e}")
                        pass
                else:
                    if png_file:
                        print(f"⚠ PNG file not found for {eq_id}: {png_file}")
                    else:
                        print(f"○ No PNG file specified for {eq_id}")
                
                self.equation_list.addItem(item)
                print(f"Debug: Added item for {eq_id} to list")
            
            print(f"Debug: Total items in equation list: {self.equation_list.count()}")
            
        except Exception as e:
            print(f"Debug: Exception in load_equations: {e}")
            makeMessageBox(f"Error loading equations: {str(e)}")
    
    def on_method_changed(self):
        """Handle definition method change"""
        use_equation = self.equation_radio.isChecked()
        
        self.equation_group.setVisible(use_equation)
        self.initialization_group.setVisible(not use_equation)
        
        # Update OK button state
        self.update_ok_button_state()
    
    def on_equation_selection_changed(self):
        """Handle equation selection change"""
        current_item = self.equation_list.currentItem()
        if current_item:
            eq_id = current_item.data(QtCore.Qt.UserRole)
            if eq_id:
                self.selected_equation = eq_id
                self.show_equation_details(eq_id)
            else:
                self.selected_equation = None
                self.equation_details.setText("No equation selected")
        else:
            self.selected_equation = None
            self.equation_details.setText("Select an equation to see details")
        
        self.update_ok_button_state()
    
    def show_equation_details(self, eq_id):
        """Show details of the selected equation"""
        try:
            # Get equation data from ontology container's equation dictionary first
            equation_dictionary = getattr(self.ontology_container, 'equation_dictionary', {})
            eq_data = equation_dictionary.get(eq_id, {})
            
            # Fall back to variable data if not found in dictionary
            if not eq_data:
                equations = self.variable_data.get('equations', {})
                eq_data = equations.get(eq_id, {})
            
            eq_label = eq_data.get('label', f'Equation_{eq_id}')
            eq_expression = eq_data.get('expression', 'No expression')
            eq_description = eq_data.get('description', 'No description available')
            
            details_text = f"<b>{eq_label}</b><br>"
            details_text += f"<b>Expression:</b> {eq_expression}<br>"
            details_text += f"<b>Description:</b> {eq_description}"
            
            self.equation_details.setText(details_text)
            
        except Exception as e:
            self.equation_details.setText(f"Error loading equation details: {str(e)}")
    
    def update_ok_button_state(self):
        """Update the OK button enabled state"""
        if self.equation_radio.isChecked():
            # Need selected equation
            self.ok_button.setEnabled(self.selected_equation is not None)
        else:
            # Need initialization value
            text = self.init_value_input.text().strip()
            self.ok_button.setEnabled(len(text) > 0)
    
    def accept_selection(self):
        """Accept the current selection"""
        if self.equation_radio.isChecked():
            self.use_initialization = False
            self.initialization_value = None
        else:
            self.use_initialization = True
            self.initialization_value = self.init_value_input.text().strip()
        
        self.accept()
    
    def get_selection(self):
        """Get the selection result"""
        return {
            'equation_id': self.selected_equation,
            'use_initialization': self.use_initialization,
            'initialization_value': self.initialization_value
        }


def select_equation_for_variable(variable_data, ontology_container):
    """
    Launch the equation selector dialog for a variable.
    
    Args:
        variable_data: Dictionary containing variable information
        ontology_container: The ontology container
        
    Returns:
        Dictionary with selection results or None if cancelled
    """
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    
    dialog = EquationSelectorDialog(variable_data, ontology_container)
    
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        return dialog.get_selection()
    
    return None
