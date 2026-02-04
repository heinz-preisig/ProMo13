#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
Behavior Association Editor for CAM12/ProMo
===============================================================================

This module provides the variable-equation tree building functionality
adapted from CAM10 BehaviorAssociation for integration with CAM12 BehaviourLinker_v01.
"""

import os
import sys
from copy import deepcopy
from os.path import join

# Add the packages directory to Python path to resolve Common imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from Common.common_resources import getData
from Common.common_resources import getOntologyName
from Common.common_resources import indexList
from Common.common_resources import putData
from Common.common_resources import TEMPLATE_ENTITY_OBJECT
from Common.common_resources import walkDepthFirstFnc
from Common.exchange_board import ProMoExchangeBoard
from Common.pop_up_message_box import makeMessageBox
from Common.record_definitions_equation_linking import EntityBehaviour
from Common.record_definitions_equation_linking import functionGetObjectsFromObjectStringID
from Common.record_definitions_equation_linking import functionMakeObjectStringID
from Common.record_definitions_equation_linking import VariantRecord
from Common.resource_initialisation import checkAndFixResources
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES
from Common.resources_icons import roundButton
from Common.ui_number_dialog_impl import UI_String
from Common.ui_two_list_selector_dialog_impl import UI_TwoListSelector
from OntologyBuilder.BehaviourLinker_v01.behaviour_association.equation_selector import select_equation_for_variable

# Import the required classes from CAM10 resources
# These will need to be adapted for CAM12
try:
    from OntologyBuilder.OntologyEquationEditor.resources import AnalyseBiPartiteGraph
    from OntologyBuilder.OntologyEquationEditor.resources import isVariableInExpression
    from OntologyBuilder.OntologyEquationEditor.resources import makeLatexDoc
    from OntologyBuilder.OntologyEquationEditor.resources import renderExpressionFromGlobalIDToInternal
    from OntologyBuilder.OntologyEquationEditor.resources import showPDF
    from OntologyBuilder.OntologyEquationEditor.variable_framework import findDependentVariables
    from OntologyBuilder.OntologyEquationEditor.variable_framework import makeIncidenceDictionaries
except ImportError:
    # Fallback for CAM12 - these will need to be implemented
    pass

# Fallback functions for CAM12 - these will need to be implemented
def AnalyseBiPartiteGraph(*args, **kwargs):
    raise NotImplementedError("AnalyseBiPartiteGraph needs to be adapted for CAM12")

def isVariableInExpression(*args, **kwargs):
    raise NotImplementedError("isVariableInExpression needs to be adapted for CAM12")

def makeLatexDoc(*args, **kwargs):
    raise NotImplementedError("makeLatexDoc needs to be adapted for CAM12")

def renderExpressionFromGlobalIDToInternal(*args, **kwargs):
    raise NotImplementedError("renderExpressionFromGlobalIDToInternal needs to be adapted for CAM12")

def showPDF(*args, **kwargs):
    raise NotImplementedError("showPDF needs to be adapted for CAM12")

def findDependentVariables(*args, **kwargs):
    raise NotImplementedError("findDependentVariables needs to be adapted for CAM12")

def makeIncidenceDictionaries(*args, **kwargs):
    raise NotImplementedError("makeIncidenceDictionaries needs to be adapted for CAM12")


base_variant = "base"  # RULE: nomenclature for base case
pixel_or_text = "text"  # NOTE: variable to set the mode


class Selector(QtCore.QObject):
    """
    Generates a selector for a set of radio buttons.
    The radio buttons are added to a given layout.
    Layouts are handling the buttons in autoexclusive mode.
    """
    radio_signal = QtCore.pyqtSignal(str, int)

    def __init__(self, radio_class, receiver, label_list, layout, mode="text", autoexclusive=True):
        super().__init__()
        self.radio_class = radio_class
        self.labels = label_list
        self.layout = layout
        self.mode = mode
        self.autoexclusive = autoexclusive
        self.selected_ID = None
        self.show_list = []

        self.radios = {}
        self.label_indices, \
        self.label_indices_inverse = indexList(self.labels)

        self.makeSelector()
        self.radio_signal.connect(receiver)

    def makeSelector(self):
        if self.mode == "text":
            self.makeTextSelector()
        else:
            raise NotImplementedError("Pixel selector not implemented")

    def makeTextSelector(self):
        for ID in self.label_indices:
            label = self.labels[ID]
            self.radios[ID] = QtWidgets.QCheckBox(label)
            self.layout.addWidget(self.radios[ID])
            self.radios[ID].toggled.connect(self.selector_toggled)

    def selector_toggled(self, toggled):
        if toggled:
            ID = self.getToggled()
            if ID >= 0:
                self.radio_signal.emit(self.radio_class, ID)

    def getToggled(self):
        count = -1
        ID = -1
        for ID_ in self.radios:
            count += 1
            if self.radios[ID_].isChecked():
                ID = count
                self.radios[ID].setCheckState(False)
        self.selected_ID = ID
        return ID

    def getStrID(self):
        ID = self.selected_ID
        if ID == None:
            return None
        return self.label_indices[ID]


class BehaviorAssociationEditor(QtWidgets.QMainWindow):
    """
    Simplified BehaviorAssociation editor for CAM12/ProMo
    Integrates with the existing EntityEditorFrontEnd
    """
    
    # Signal to communicate back to the entity editor
    behavior_defined = QtCore.pyqtSignal(dict)
    # Add signal for cancellation
    cancelled = QtCore.pyqtSignal()
    
    def __init__(self, ontology_container, parent=None):
        super().__init__(parent)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        
        self.ontology_container = ontology_container
        self.ontology_name = ontology_container.ontology_name
        
        # Setup basic UI
        self.setWindowTitle("Behavior Association Editor")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Add title
        title = QtWidgets.QLabel("Select Variable to Start Entity Definition")
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Variable selection area with enhanced display for LaTeX images
        self.variable_list = QtWidgets.QListWidget()
        self.variable_list.setIconSize(QtCore.QSize(200, 60))  # Larger size for LaTeX images
        self.variable_list.setSpacing(8)  # More spacing between items
        self.variable_list.setUniformItemSizes(True)
        
        # Set item size to accommodate both image and text
        self.variable_list.setGridSize(QtCore.QSize(400, 80))
        
        layout.addWidget(self.variable_list)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.select_button = QtWidgets.QPushButton("Select & Build Tree")
        self.select_button.clicked.connect(self.select_variable_and_build_tree)
        button_layout.addWidget(self.select_button)
        
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_and_close)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Status label (instead of statusbar since this is embedded in a dialog)
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet("QLabel { color: gray; font-style: italic; margin: 5px; }")
        layout.addWidget(self.status_label)
        
        # Load variables
        self.load_variables()
        
        # Store results
        self.entity_assignments = None
    
    def cancel_and_close(self):
        """Handle cancellation and emit cancelled signal"""
        self.cancelled.emit()
        self.close()
    
    def closeEvent(self, event):
        """Handle close event to ensure cancellation is handled"""
        # If no assignments were made, this is a cancellation
        if self.entity_assignments is None:
            self.cancelled.emit()
        super().closeEvent(event)
    
    def load_variables(self):
        """Load available variables from the ontology container with LaTeX PNG images"""
        try:
            variables = self.ontology_container.variables
            self.variable_list.clear()
            
            print(f"Debug: Loading {len(variables)} variables from ontology")
            
            # # Count variables with label "T"
            # t_variables = []
            # for var_id in variables:
            #     var_data = variables[var_id]
            #     if var_data.get('label') == 'T':
            #         t_variables.append(var_id)
            #
            # print(f"Debug: Found {len(t_variables)} variables with label 'T': {t_variables}")
            
            for var_id in variables:
                var_data = variables[var_id]
                label = var_data.get('label', f'Variable_{var_id}')
                var_type = var_data.get('type', 'unknown')
                network = var_data.get('network', 'unknown')
                png_file = var_data.get('png_file')  # PNG path now stored directly in variable
                
                # # Debug for T variables
                # if label == 'T':
                #     print(f"Debug: T variable found - ID: {var_id}, Network: {network}, Equations: {list(var_data.get('equations', {}).keys())}, PNG: {png_file}")
                
                # Create list item with text
                item_text = f"{label}\n(ID: {var_id}, Type: {var_type}, Network: {network})"
                item = QtWidgets.QListWidgetItem(item_text)
                item.setData(QtCore.Qt.UserRole, var_id)
                
                # Add LaTeX PNG image if available
                if png_file and os.path.exists(png_file):
                    try:
                        icon = QtGui.QIcon(png_file)
                        if not icon.isNull():
                            item.setIcon(icon)
                    except Exception as e:
                        pass
                
                self.variable_list.addItem(item)
            
            print(f"Debug: Total variables loaded: {self.variable_list.count()}")
                
        except Exception as e:
            print(f"Debug: Error loading variables: {e}")
            makeMessageBox(f"Error loading variables: {str(e)}")
    
    def select_variable_and_build_tree(self):
        """Select the current variable and build the behavior tree"""
        current_item = self.variable_list.currentItem()
        if not current_item:
            makeMessageBox("Please select a variable first")
            return
        
        var_id = current_item.data(QtCore.Qt.UserRole)
        var_data = self.ontology_container.variables[var_id]
        
        print(f"Debug: Selected variable - ID: {var_id}")
        print(f"Debug: Selected variable - Label: {var_data.get('label')}")
        print(f"Debug: Selected variable - Network: {var_data.get('network')}")
        print(f"Debug: Selected variable - Equations: {list(var_data.get('equations', {}).keys())}")
        print(f"Debug: Selected variable - Number of equations: {len(var_data.get('equations', {}))}")
        
        try:
            # First, let the user select the equation or initialization method
            equation_selection = select_equation_for_variable(var_data, self.ontology_container)
            
            if equation_selection is None:
                # User cancelled the selection
                return
            
            # Build the bipartite graph tree with the selected equation
            self.build_behavior_tree(var_id, var_data, equation_selection)
            
        except Exception as e:
            print(f"Debug: Error in select_variable_and_build_tree: {e}")
            makeMessageBox(f"Error building behavior tree: {str(e)}")
    
    def build_behavior_tree(self, var_id, var_data, equation_selection):
        """Build the behavior tree using the selected variable and equation"""
        try:
            # For now, create a simple assignment structure
            # This will need to be replaced with the actual AnalyseBiPartiteGraph call
            
            self.entity_assignments = {
                'root_variable': var_id,
                'root_equation': equation_selection.get('equation_id'),
                'use_initialization': equation_selection.get('use_initialization', False),
                'tree': {0: {'children': [], 'parent': None}},
                'nodes': {0: f'variable_{var_id}'},
                'IDs': {f'variable_{var_id}': 0},
                'blocked_list': [],
                'buddies_list': []
            }
            
            # If using equation definition, add the equation to the tree
            if not equation_selection.get('use_initialization', False):
                eq_id = equation_selection.get('equation_id')
                if eq_id:
                    # Add equation to tree
                    node_id = 1
                    self.entity_assignments['tree'][0]['children'].append(node_id)
                    self.entity_assignments['tree'][node_id] = {'children': [], 'parent': 0}
                    self.entity_assignments['nodes'][node_id] = f'equation_{eq_id}'
                    self.entity_assignments['IDs'][f'equation_{eq_id}'] = node_id
            else:
                # Using initialization, no equation in tree
                self.entity_assignments['root_equation'] = None
            
            # Show success message
            if equation_selection.get('use_initialization', False):
                var_label = var_data.get('label', var_id)
                self.status_label.setText(f"Variable '{var_label}' marked for initialization")
                print(f"Debug: Variable {var_label} marked for initialization")
            else:
                eq_id = equation_selection.get('equation_id', 'unknown')
                var_label = var_data.get('label', var_id)
                self.status_label.setText(f"Variable '{var_label}' defined with equation {eq_id}")
                print(f"Debug: Variable {var_label} defined with equation {eq_id}")
            
            # Emit signal with the assignments
            self.behavior_defined.emit(self.entity_assignments)
            
            # Close the editor
            self.close()
            
        except Exception as e:
            makeMessageBox(f"Error building tree: {str(e)}")
    
    def get_assignments(self):
        """Return the generated entity assignments"""
        return self.entity_assignments


def launch_behavior_association_editor(ontology_container):
    """
    Launch the BehaviorAssociation editor
    
    Args:
        ontology_container: The ontology container with variables and equations
        
    Returns:
        The entity assignments if defined, None otherwise
    """
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    else:
        # Ensure the existing app has proper GUI support for images
        # This helps with PNG loading in dialogs
        app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    
    editor = BehaviorAssociationEditor(ontology_container)
    
    # Create a modal dialog to wait for result
    dialog = QtWidgets.QDialog()
    dialog.setLayout(QtWidgets.QVBoxLayout())
    dialog.layout().addWidget(editor)
    
    assignments = None
    
    def on_behavior_defined(result):
        nonlocal assignments
        assignments = result
        dialog.accept()
    
    def on_cancelled():
        # Handle cancellation explicitly
        assignments = None
        dialog.reject()
    
    # Connect both signals
    editor.behavior_defined.connect(on_behavior_defined)
    editor.cancelled.connect(on_cancelled)
    
    # Set dialog properties
    dialog.setWindowTitle("Behavior Association Editor")
    dialog.setModal(True)
    dialog.resize(800, 600)
    
    # Execute dialog and return result
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        return assignments
    else:
        return None
