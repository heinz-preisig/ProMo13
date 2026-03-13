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

# Add the packages directory to Python path to resolve Common imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from PyQt5 import QtCore, QtGui, QtWidgets

from Common.common_resources import indexList
from Common.pop_up_message_box import makeMessageBox
from OntologyBuilder.BehaviourLinker_v01.behaviour_association.equation_selector import select_equation_for_variable
from OntologyBuilder.BehaviourLinker_v01.variable_classification_rules import VariableClassificationRules
from OntologyBuilder.BehaviourLinker_v01.ui_settings import UISettings
from OntologyBuilder.BehaviourLinker_v01.UIs.variable_selection import Ui_Dialog


# Error logging utility
def log_error(method_name: str, error: Exception, context: str = ""):
    """Log error with method name and context for debugging"""
    error_msg = f"ERROR in {method_name}"
    if context:
        error_msg += f" ({context})"
    error_msg += f": {str(error)}"
    print(error_msg)  # Keep console output for debugging


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


class BehaviorAssociationEditor(QtWidgets.QDialog):
    """
    Simplified BehaviorAssociation editor for CAM12/ProMo
    Integrates with the existing EntityEditorFrontEnd
    """

    # Signal to communicate back to the entity editor
    behavior_defined = QtCore.pyqtSignal(dict)
    # Add signal for cancellation
    cancelled = QtCore.pyqtSignal()

    def __init__(self, ontology_container, entity_type_info=None, variable_class_mode='state', current_entity=None,
                 parent=None):
        super().__init__(parent)

        # Use normal dialog window to avoid cancel/close issues
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)

        # Also set window attributes for frameless
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, False)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, False)

        # Setup UI using the UI file
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Ensure the UI respects frameless window
        self.ui.listVariables.setFocus()

        self.ontology_container = ontology_container
        self.ontology_name = ontology_container.ontology_name
        self.entity_type_info = entity_type_info or {}  # Store entity type info for rules
        self.variable_class_mode = variable_class_mode  # Store variable class mode
        self.current_entity = current_entity  # Store current entity for filtering

        # Preload variable icons for better performance
        self.preloaded_variable_icons = {}
        self._preload_variable_icons()

        # Set window title based on variable class mode
        if variable_class_mode == 'state':
            self.setWindowTitle("Select State Variable to Start Entity Definition")
        elif variable_class_mode == 'definable':
            self.setWindowTitle("Add Variable (Only definable from existing variables)")
        elif variable_class_mode == 'transport':
            self.setWindowTitle("Add Variable (Select from transport variables)")
        elif variable_class_mode == 'intensity':
            self.setWindowTitle("Add Intensity Variable (Secondary state variables for reservoirs)")
        else:
            self.setWindowTitle("Select Variable to Add to Entity Definition")

        # Configure the variable list using UISettings
        UISettings.configure_list_widget(self.ui.listVariables, 'variable_selection')

        # Additional QListView-specific configuration for icon display
        # Note: Icon size is already set by UISettings.configure_list_widget() above
        self.ui.listVariables.setUniformItemSizes(True)  # Ensure uniform item sizes
        self.ui.listVariables.setViewMode(QtWidgets.QListView.ListMode)  # Ensure list mode

        # Enable size adjustment to fit content
        self.ui.listVariables.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.ui.listVariables.setMinimumHeight(200)  # Set minimum height
        self.ui.listVariables.setMinimumWidth(400)  # Set minimum width

        # Connect signals
        self.ui.pushCancel.clicked.connect(self.cancel_and_close)

        # Store reference for easier access
        self.variable_list = self.ui.listVariables
        self.cancel_button = self.ui.pushCancel

        # Use status label from UI file - it's already positioned correctly
        self.status_label = self.ui.statusLabel
        self.status_label.setStyleSheet("QLabel { color: gray; font-style: italic; margin: 5px; }")
        self.status_label.setText("Ready")

        # Connect double-click for direct variable selection
        self.ui.listVariables.doubleClicked.connect(self.on_variable_double_clicked)

        # Connect single-click for variable selection (highlighting)
        self.ui.listVariables.clicked.connect(self.on_variable_clicked)

        # Load variables
        self.load_variables()

        # Store results
        self.entity_assignments = None

    def on_variable_clicked(self, index):
        """Handle single-click on variable - just highlight and show info"""
        try:
            # Get the selected item
            item = self.ui.listVariables.model().itemFromIndex(index)
            if item:
                # Get variable data from the item
                var_id = item.data(QtCore.Qt.UserRole)
                if var_id:
                    self.status_label.setText(f"Selected: {var_id} (double-click to select equation)")
                else:
                    self.status_label.setText("No variable data found")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def on_variable_double_clicked(self, index):
        """Handle double-click on variable - go directly to equation selection"""
        try:
            # Get the selected item
            item = self.ui.listVariables.model().itemFromIndex(index)
            if item:
                # Get variable data from the item
                var_id = item.data(QtCore.Qt.UserRole)
                if var_id:
                    self.status_label.setText(f"Selected variable: {var_id}")

                    # Directly proceed to equation selection for this variable
                    self.select_variable_and_build_tree()
                else:
                    self.status_label.setText("No variable data found")
        except Exception as e:
            log_error("on_listVariables_doubleClicked", e, "handling variable double-click")
            self.status_label.setText(f"Error: {str(e)}")

    def _preload_variable_icons(self):
        """Preload variable PNG icons using exchange board for consistency"""
        try:
            # Check if ontology_container is available
            if self.ontology_container is None:
                self.preloaded_variable_icons = {}
                return

            # Use the existing ontology container to load all variable icons
            self.preloaded_variable_icons = self.ontology_container.load_variable_icons()

        except Exception as e:
            self.preloaded_variable_icons = {}
            log_error("_preload_variable_icons", e, "preloading variable icons")

    def mousePressEvent(self, event):
        """Make frameless window draggable"""
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle window dragging"""
        if event.buttons() == QtCore.Qt.LeftButton and hasattr(self, 'drag_pos'):
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Clean up drag position"""
        if hasattr(self, 'drag_pos'):
            delattr(self, 'drag_pos')

    def cancel_and_close(self):
        """Handle cancellation and emit cancelled signal"""
        self.cancelled.emit()
        self.reject()

    def closeEvent(self, event):
        """Handle close event"""
        event.accept()

    def load_variables(self):
        """Load available variables from the ontology container with filtering based on entity type rules"""
        try:
            variables = self.ontology_container.variables

            # Clear the list using QListView model (QListView doesn't have clear() method)
            model = QtGui.QStandardItemModel()
            self.variable_list.setModel(model)

            # Convert variables to list format for rule processing
            variable_list = []
            for var_id, var_data in variables.items():
                try:
                    # Safely get png_file - handle None or invalid values
                    png_file = var_data.get('png_file')
                    if png_file == 'None' or png_file is None or png_file == '':
                        png_file = None
                    
                    # Safely get equations - handle None or invalid values
                    equations_data = var_data.get('equations', {})
                    if equations_data is None:
                        equations_data = {}
                    elif not isinstance(equations_data, dict):
                        # If equations is not a dict, try to handle it gracefully
                        equations_data = {}
                    
                    equations_list = list(equations_data.keys()) if equations_data else []
                    
                    var_info = {
                            'id'       : var_id,
                            'label'    : var_data.get('label', f'Variable_{var_id}'),
                            'type'     : var_data.get('type', 'unknown'),
                            'network'  : var_data.get('network', 'unknown'),
                            'category' : var_data.get('category', 'unknown'),
                            'equations': equations_list,
                            'png_file' : png_file,
                            'data'     : var_data  # Store full data for later use
                            }
                    variable_list.append(var_info)
                    
                except Exception as e:
                    # Skip problematic variables but continue loading others
                    print(f"Warning: Skipping variable {var_id} due to error: {e}")
                    continue

            # Apply filtering rules based on entity type
            filtered_variables = self._filter_variables_by_rules(variable_list)

            # Load filtered variables into the list
            for var_info in filtered_variables:
                var_id = var_info['id']
                label = var_info['label']
                var_type = var_info['type']
                network = var_info['network']
                png_file = var_info['png_file']

                # Create list item with text
                item_text = f"{label}\n(ID: {var_id}, Type: {var_type}, Network: {network})"
                item_text = f"     {var_id} -- {var_type} in {network}"
                item = QtGui.QStandardItem(item_text)
                item.setData(var_id, QtCore.Qt.UserRole)

                # Add icon using preloaded variable icons from exchange board
                if var_id in self.preloaded_variable_icons:
                    item.setIcon(self.preloaded_variable_icons[var_id])
                else:
                    log_error("load_variables", Exception(f"No icon for variable {var_id}"),
                              f"no icon found for variable {var_id}")

                # Add item to model
                model.appendRow(item)

            # Adjust size to fit content after loading
            self.adjust_list_view_size()

            self.status_label.setText(f"Loaded {len(filtered_variables)} variables")

        except Exception as e:
            error_msg = f"Error loading variables: {str(e)}"
            print(f"DEBUG: Variable loading error details: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()  # Print full stack trace for debugging
            log_error("load_variables", e, "loading variables")
            self.status_label.setText(error_msg)
            makeMessageBox(error_msg)

    def adjust_list_view_size(self):
        """Adjust QListView size based on content"""
        try:
            model = self.ui.listVariables.model()
            if not model:
                return

            # Calculate optimal height based on number of items
            item_count = model.rowCount()
            if item_count == 0:
                return

            # Get the actual icon size from UI settings or current widget
            icon_size = self.ui.listVariables.iconSize()
            icon_height = icon_size.height()

            # Get font metrics for height calculation
            font_metrics = QtGui.QFontMetrics(self.ui.listVariables.font())
            text_height = font_metrics.height() + 8  # Text height + padding

            # Use the larger of icon height or text height
            item_height = max(icon_height, text_height)

            # Calculate total height with some padding
            total_height = item_height * item_count + 20  # 20px padding

            # Calculate width based on content
            max_width = 400
            for row in range(item_count):
                item = model.item(row)
                if item:
                    text_width = font_metrics.width(item.text()) + icon_size.width() + 20  # icon width + padding
                    max_width = max(max_width, text_width)

            # Set the size (but respect reasonable limits)
            max_height = min(total_height, 400)  # Max 400px height
            max_width = min(max_width, 600)  # Max 600px width

            self.ui.listVariables.setMinimumHeight(min(200, max_height))
            self.ui.listVariables.setMinimumWidth(min(400, max_width))


        except Exception as e:
            log_error("adjust_list_view_size", e, "adjusting list view size")

    def _get_definable_variables_graph_based(self, variables, already_included, already_defined):
        """
        Find variables that can be defined by equations using only already included variables.
        
        Uses entity's own equations and dependencies lists for direct dependency analysis.
        No UI dependencies - pure input → output function.
        
        Args:
            variables (list): All available variables from ontology
            already_included (set): Variables already included in entity
            already_defined (set): Variables already defined in entity
            
        Returns:
            list: Variables that can be defined from already included variables
        """
        definable_variables = []

        # Build dependency graph from dependencies lists
        newly_definable = set()

        # find set of constants
        constant_vars = set()
        for var in variables:
            type = var["data"]["type"]
            if type == "constant":
                constant_vars.add(var["id"])

            pass

        equations = self.current_entity.all_equations
        for eq_id, equation in equations.items():
            dependencies_set = set(equation.get_dependencies_list())
            lhs = equation.lhs["global_ID"]
            reduced_dependencies_set = dependencies_set - (dependencies_set and constant_vars)

            # If all required variables are available and LHS not already defined
            if reduced_dependencies_set.issubset(already_included) and (lhs not in already_included) and (
                    lhs not in already_defined):
                newly_definable.add(lhs)

        # Convert definable variable IDs to variable info objects
        for var_info in variables:
            if var_info['id'] in newly_definable:
                definable_variables.append(var_info)

        return definable_variables

    def _get_equation_required_variables(self, equation):
        """
        Extract the variables required by an equation (variables on RHS).
        
        Args:
            equation: Equation object or dictionary
            
        Returns:
            set: Set of variable IDs required by this equation
        """
        required_vars = set()

        try:
            # Try to use the proper variable extraction method if available
            try:
                from OntologyBuilder.OntologyEquationEditor.variable_framework import findDependentVariables
                if hasattr(equation, 'getIncidenceList'):
                    # Use the proper method to get dependent variables
                    dependent_vars = findDependentVariables(equation)
                    for var in dependent_vars:
                        if var.startswith('V_'):
                            required_vars.add(var)
                    return required_vars
            except ImportError:
                pass  # Fallback to manual parsing if import fails

            # Handle different equation formats (fallback)
            if hasattr(equation, 'rhs') and hasattr(equation.rhs, 'get'):
                # Equation object with rhs dict
                rhs_content = equation.rhs.get('global_ID', '')
                # Split by whitespace and filter for variable IDs (starting with V_)
                terms = rhs_content.split()
                for term in terms:
                    if term.startswith('V_'):
                        required_vars.add(term)

            elif isinstance(equation, dict) and 'rhs' in equation:
                # Equation dictionary
                rhs = equation['rhs']
                if isinstance(rhs, dict) and 'global_ID' in rhs:
                    terms = rhs['global_ID'].split()
                    for term in terms:
                        if term.startswith('V_'):
                            required_vars.add(term)
                elif isinstance(rhs, str):
                    terms = rhs.split()
                    for term in terms:
                        if term.startswith('V_'):
                            required_vars.add(term)

        except Exception as e:
            log_error("_get_equation_required_variables", e, f"extracting required variables from equation")

        return required_vars

    def _filter_variables_by_rules(self, variables):  # RULE: for filtering the variables
        """Filter variables based on entity type rules and exclude already included variables"""
        if not self.entity_type_info:
            # No entity type info, return all variables
            return variables

        # Use exchange board's unified filtering method
        try:
            filtered_variables = self.ontology_container.filter_variables_for_behaviour_linker(
                self.entity_type_info, 
                self.variable_class_mode
            )
            
            # Remove already included variables if current_entity is available
            if self.current_entity is not None:
                already_included = set(self.current_entity.get_entity_variables())
                filtered_variables = [var for var in filtered_variables if var['id'] not in already_included]
            
            return filtered_variables
            
        except Exception as e:
            print(f"Error using exchange board filtering, falling back to original method: {e}")
            # Fallback to original method if exchange board filtering fails
            return self._filter_variables_by_rules_original(variables)
    
    def _filter_variables_by_rules_original(self, variables):  # Original method as fallback
        """Original filtering method as fallback"""
        # First, get variables already defined in current entity
        # Use current entity's actual state, not recompute
        classification = VariableClassificationRules.classify_variables(variables, self.entity_type_info)

        # Filter based on variable class mode
        if self.variable_class_mode == 'state':
            # State variable mode: only show allowed root variables (typically state variables)
            filtered_variables = classification['allowed_root']
        elif self.variable_class_mode == 'transport':
            # Transport mode: show only transport variables (for arcs)
            filtered_variables = VariableClassificationRules.filter_variables_by_type(variables, ['transport'])
        elif self.variable_class_mode == 'intensity':
            # Intensity mode: show secondary state variables suitable for reservoirs
            # Filter for variables that can be used as intensity/secondary states
            filtered_variables = VariableClassificationRules.filter_variables_by_type(variables,
                                                                                      ['effort', 'secondaryState'])
        elif self.variable_class_mode == 'all':
            # All variables mode: show all variables applicable to the network
            # Combine all classifications but remove duplicates
            all_variables = (classification['allowed_root'] +
                             classification['inputs'] +
                             classification['outputs'])

            # Remove duplicates while preserving order
            seen_ids = set()
            filtered_variables = []
            for var in all_variables:
                if var['id'] not in seen_ids:
                    seen_ids.add(var['id'])
                    filtered_variables.append(var)

        elif self.variable_class_mode == 'definable':
            # Definable variables mode: only show variables that can be defined from already included variables
            already_included = set(self.current_entity.get_entity_variables())
            entity = self.current_entity
            inputs = entity.get_input_vars()
            outputs = entity.get_output_vars(self.ontology_container)
            instances = entity.get_variables_to_be_instantiated()
            equation_defined = entity.get_equation_defined_vars(self.ontology_container)
            already_defined_variables = set(inputs + outputs + instances + equation_defined)

            filtered_variables = self._get_definable_variables_graph_based(variables, already_included,
                                                                           already_defined_variables)
        else:
            # Default to state mode for unknown modes
            filtered_variables = classification['allowed_root']

        return filtered_variables

    def select_variable_and_build_tree(self):
        """Select the current variable and build the behavior tree"""
        selection_model = self.variable_list.selectionModel()
        selected_indexes = selection_model.selectedIndexes()

        if not selected_indexes:
            makeMessageBox("Please select a variable first")
            return

        # Get the selected index and item
        selected_index = selected_indexes[0]
        model = self.variable_list.model()
        item = model.itemFromIndex(selected_index)

        if not item:
            makeMessageBox("No item found for selection")
            return

        var_id = item.data(QtCore.Qt.UserRole)
        var_data = self.ontology_container.variables[var_id]

        try:
            # First, let the user select the equation or initialization method
            equation_selection = select_equation_for_variable(var_data, self.ontology_container)

            if equation_selection is None:
                # User cancelled the selection
                return

            # Build the bipartite graph tree with the selected equation
            self.build_behavior_tree(var_id, var_data, equation_selection)

        except Exception as e:
            log_error("select_variable_and_build_tree", e, "building behavior tree")
            makeMessageBox(f"Error building behavior tree: {str(e)}")

    def build_behavior_tree(self, var_id, var_data, equation_selection):
        """Build the behavior tree using the selected variable and equation"""
        try:
            # For now, create a simple assignment structure
            # This will need to be replaced with the actual AnalyseBiPartiteGraph call

            self.entity_assignments = {
                    'root_variable'     : var_id,
                    'root_equation'     : equation_selection.get('equation_id'),
                    'use_initialization': equation_selection.get('use_initialization', False),
                    'tree'              : {0: {'children': [], 'parent': None}},
                    'nodes'             : {0: var_id},
                    'IDs'               : {var_id: 0},
                    'blocked_list'      : [],
                    'buddies_list'      : []
                    }

            # If using equation definition, add the equation to the tree
            if not equation_selection.get('use_initialization', False):
                eq_id = equation_selection.get('equation_id')
                if eq_id:
                    # Add equation to tree
                    node_id = 1
                    self.entity_assignments['tree'][0]['children'].append(node_id)
                    self.entity_assignments['tree'][node_id] = {'children': [], 'parent': 0}
                    self.entity_assignments['nodes'][node_id] = eq_id
                    self.entity_assignments['IDs'][eq_id] = node_id
            else:
                # Using initialization, no equation in tree
                self.entity_assignments['root_equation'] = None

            # Show success message
            if equation_selection.get('use_initialization', False):
                var_label = var_data.get('label', var_id)
                self.status_label.setText(f"Variable '{var_label}' marked for initialization")
            else:
                eq_id = equation_selection.get('equation_id', 'unknown')
                var_label = var_data.get('label', var_id)
                self.status_label.setText(f"Variable '{var_label}' defined with equation {eq_id}")

            # Emit signal with the assignments
            self.behavior_defined.emit(self.entity_assignments)

            # Close the editor with accept
            self.accept()

        except Exception as e:
            makeMessageBox(f"Error building tree: {str(e)}")

    def get_assignments(self):
        """Return the generated entity assignments"""
        return self.entity_assignments


def launch_behavior_association_editor(ontology_container, entity_type_info=None, variable_class_mode='state',
                                       current_entity=None):
    """
    Launch the BehaviorAssociation editor
    
    Args:
        ontology_container: The ontology container with variables and equations
        entity_type_info: Dictionary containing network, category, entity_type for rule-based filtering
        variable_class_mode: 'state' for state variables only, 'all' for all applicable variables, 
                           'definable' for variables definable from existing ones,
                           'transport' for transport variables, 'intensity' for secondary state variables
        current_entity: The current entity object to filter out already included variables
        
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

    editor = BehaviorAssociationEditor(ontology_container, entity_type_info, variable_class_mode, current_entity)

    assignments = None

    def on_behavior_defined(result):
        nonlocal assignments
        assignments = result
        editor.accept()

    def on_cancelled():
        nonlocal assignments
        assignments = None
        # Don't call reject here - let the cancel button handle it
        # This prevents double handling and prompts

    # Connect the signals to handle results
    editor.behavior_defined.connect(on_behavior_defined)
    editor.cancelled.connect(on_cancelled)

    # Set modal explicitly to ensure proper dialog behavior
    editor.setModal(True)

    # Execute the dialog and get the result
    result = editor.exec_()

    # If dialog was rejected (cancelled), ensure assignments is None
    if result == QtWidgets.QDialog.Rejected:
        assignments = None

    return assignments
