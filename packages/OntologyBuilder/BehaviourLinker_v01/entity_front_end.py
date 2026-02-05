#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
GUI for automata editor

Automata control the user interface of the ModelComposer
===============================================================================
"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2026. 01. 23"
__license__ = "GPL planned -- until further notice for internal Bio4Fuel & MarketPlace use only"
__version__ = "12"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import sys

from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel

from Common.resources_icons import roundButton, getIcon
from OntologyBuilder.BehaviourLinker_v01.UIs.entity_changes import Ui_entity_changes
from OntologyBuilder.BehaviourLinker_v01.resources.pop_up_message_box import makeMessageBox
from OntologyBuilder.BehaviourLinker_v01.ui_settings import UISettings
# from OntologyBuilder.BehaviourLinker_v01.behaviour_association.editor import launch_behavior_association_editor

class EntityEditorFrontEnd(QtWidgets.QDialog):
    """
     make new and edit entity instances

    """
    message = pyqtSignal(dict)

    # setting up GUI --------------------------------------------------------------
    def __init__(self):
        super().__init__()
        self.ui = Ui_entity_changes()
        self.ui.setupUi(self)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)


        roundButton(self.ui.pushAddVariable, "new", tooltip="new variable")
        roundButton(self.ui.pushEditVariable, "edit", tooltip="edit variable")
        roundButton(self.ui.pushDeleteVariable, "delete", tooltip="delete variable")
        roundButton(self.ui.pushDeleteEntity, "delete", tooltip="delete entity")
        roundButton(self.ui.pushAccept, "accept", tooltip="accept")
        roundButton(self.ui.pushCancle, "cancel", tooltip="cancel")
        #
        #
        self.signalButton = roundButton(self.ui.LED, "LED_green", tooltip="status", mysize=20)
        
        # Add status label to the grid layout since verticalLayout_2 doesn't exist
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setStyleSheet("QLabel { color: gray; font-style: italic; margin: 5px; }")
        # Add to the bottom of the grid layout (row 7, spanning all columns)
        self.ui.gridLayout.addWidget(self.status_label, 7, 0, 1, 3)

        self.interfaceComponents()
        self.mode = "load"
        self.ontology_container = None
        self.selected_entity_type = None
        self.current_entity_data = None
        self.changed = False

    def interfaceComponents(self):
        self.gui_objects = {
                "buttons"  : {
                        "accept"   : self.ui.pushAccept,
                        "add_variable": self.ui.pushAddVariable,
                        "candle": self.ui.pushCancle,
                        "delete_entity": self.ui.pushDeleteEntity,
                        "delete_variable"  : self.ui.pushDeleteVariable,
                        "edit_variable"  : self.ui.pushEditVariable,
                        },
                "indicator": {
                        "LED": self.ui.LED,
                        },
                "lists"    : {
                        "list_defined_variables" : self.ui.list_defined_variables,
                        "list_not_defined_variables" : self.ui.list_not_defined_variables,
                        "list_equations"  : self.ui.list_equations,
                        "list_integrators": self.ui.list_integrators,
                        "list_input"      : self.ui.list_inputs,
                        "list_output"     : self.ui.list_outputs,
                        "list_instantiate": self.ui.list_instantiate,
                        "list_pending"    : self.ui.list_pending,
                        },
                }
        pass


    def set_ontology_container(self, ontology_container):
        """Set the ontology container for behavior association"""
        self.ontology_container = ontology_container

    def set_selected_entity_type(self, entity_type_data): #TODO: we may not need this one.
        """Set the selected entity type from the main tree"""
        self.selected_entity_type = entity_type_data
        print(f"EntityEditorFrontEnd received selected entity type: {self.selected_entity_type}")
        
        # Update the UI to show the selected entity type
        if self.selected_entity_type:
            network = self.selected_entity_type.get("network")
            category = self.selected_entity_type.get("category") 
            entity_type = self.selected_entity_type.get("entity type")
            name = self.selected_entity_type.get("name")  # This will be None for entity types, filled for instances
            
            if name:
                # An entity instance was selected - we're in edit mode
                selection_text = f"Editing: {network}.{category}.{entity_type}.{name}"
                self.status_label.setText(selection_text)
                self.status_label.setStyleSheet("QLabel { color: orange; font-weight: bold; margin: 5px; }")
                # TODO: Load entity data and populate the form fields
            else:
                # An entity type was selected - we're in create mode
                selection_text = f"Creating: {network}.{category}.{entity_type}"
                self.status_label.setText(selection_text)
                self.status_label.setStyleSheet("QLabel { color: blue; font-weight: bold; margin: 5px; }")

    def populate_entity_structure(self, entity_data):
        """Populate entity editor with the complete entity structure from class definition"""
        try:
            print(f"Populating entity structure: {entity_data}")
            
            # Clear all lists first
            self.clear_all_lists()
            
            # Populate not defined variables list (all variables initially)
            not_defined = entity_data.get('not_defined_variables', [])
            for var_info in not_defined:
                self.add_variable_to_list(self.ui.list_not_defined_variables, var_info)
            
            # Initially, defined variables list is empty
            defined = entity_data.get('defined_variables', [])
            for var_info in defined:
                self.add_variable_to_list(self.ui.list_defined_variables, var_info)
            
            # Populate equations list (initially empty)
            equations = entity_data.get('equations', [])
            for eq_info in equations:
                self.add_to_list(self.ui.list_equations, str(eq_info), getIcon("equation"))
            
            # Update status to show entity being created
            entity_name = entity_data.get('entity_name', 'Unknown Entity')
            self.status_label.setText(f"Creating entity: {entity_name}")
            self.status_label.setStyleSheet("QLabel { color: blue; font-weight: bold; margin: 5px; }")
            
            # Store entity data for later use
            self.current_entity_data = entity_data
            
            print(f"Entity structure populated with {len(not_defined)} variables to define")
            
        except Exception as e:
            print(f"Error populating entity structure: {e}")
            makeMessageBox(f"Error populating entity structure: {str(e)}")

    def populate_with_entity_data(self, entity_data):
        """Populate entity editor lists with variable and equation information"""
        try:
            print(f"Populating entity editor with data: {entity_data}")
            
            # Extract information from entity_data
            root_variable = entity_data.get('root_variable')
            definition_method = entity_data.get('definition_method')
            equation_id = entity_data.get('equation_id')
            assignments = entity_data.get('assignments', {})
            
            # If we have current entity data, update the lists
            if hasattr(self, 'current_entity_data') and self.current_entity_data:
                # Move variable from not_defined to defined lists
                not_defined_vars = self.current_entity_data.get('not_defined_variables', [])
                defined_vars = self.current_entity_data.get('defined_variables', [])
                
                # Find the variable that was just defined
                var_to_move = None
                for i, var_info in enumerate(not_defined_vars):
                    if var_info['id'] == root_variable:
                        var_to_move = not_defined_vars.pop(i)
                        defined_vars.append(var_to_move)
                        break
                
                if var_to_move:
                    # Update the lists
                    self.clear_all_lists()
                    
                    # Repopulate not defined variables
                    for var_info in not_defined_vars:
                        self.add_variable_to_list(self.ui.list_not_defined_variables, var_info)
                    
                    # Repopulate defined variables
                    for var_info in defined_vars:
                        self.add_variable_to_list(self.ui.list_defined_variables, var_info)
                    
                    # Update current entity data
                    self.current_entity_data['not_defined_variables'] = not_defined_vars
                    self.current_entity_data['defined_variables'] = defined_vars
                    
                    # Add equation if defined with equation
                    if definition_method != 'initialization' and equation_id:
                        equation_dict = getattr(self.ontology_container, 'equation_dictionary', {})
                        if equation_id in equation_dict:
                            eq_data = equation_dict[equation_id]
                            eq_label = eq_data.get('label', equation_id)
                            eq_expression = eq_data.get('expression', '')
                            self.add_to_list(self.ui.list_equations, 
                                           f"{eq_label}: {eq_expression}", getIcon("equation"))
                        else:
                            self.add_to_list(self.ui.list_equations, equation_id, getIcon("equation"))
                    
                    # Update status
                    var_label = var_to_move.get('label', root_variable)
                    if definition_method == 'initialization':
                        self.status_label.setText(f"Variable '{var_label}' marked for initialization")
                        self.status_label.setStyleSheet("QLabel { color: green; font-weight: bold; margin: 5px; }")
                    else:
                        self.status_label.setText(f"Variable '{var_label}' defined with equation {equation_id}")
                        self.status_label.setStyleSheet("QLabel { color: green; font-weight: bold; margin: 5px; }")
                    
                    # Mark as changed
                    self.markChanged()
                    
            print("Entity editor updated successfully")
            
        except Exception as e:
            print(f"Error populating entity editor: {e}")
            makeMessageBox(f"Error populating entity editor: {str(e)}")

    def clear_all_lists(self):
        """Clear all list widgets"""
        # Helper function to safely clear a list
        def safe_clear_list(list_widget):
            model = list_widget.model()
            if model is not None:
                model.clear()
            else:
                # Create and set an empty standard item model if none exists
                empty_model = QStandardItemModel()
                list_widget.setModel(empty_model)
        
        safe_clear_list(self.ui.list_defined_variables)
        safe_clear_list(self.ui.list_not_defined_variables)
        safe_clear_list(self.ui.list_inputs)
        safe_clear_list(self.ui.list_outputs)
        safe_clear_list(self.ui.list_equations)
        safe_clear_list(self.ui.list_integrators)
    
    def add_to_list(self, list_widget, text, icon=None, context='entity_lists'):
        """Add an item to a list widget with optional icon"""
        model = list_widget.model()
        if model is None:
            # Create a new standard item model
            model = QStandardItemModel()
            list_widget.setModel(model)
        
        # Always configure list widget with latest settings (to handle size changes)
        UISettings.configure_list_widget(list_widget, context)
        
        # Create item with text and optional icon
        item = QStandardItem(text)
        if icon is not None:
            item.setIcon(icon)
        model.appendRow(item)
    
    def refresh_list_widget_settings(self, list_widget, context):
        """Force refresh a list widget with new UI settings"""
        # Clear and reconfigure the list widget
        if hasattr(list_widget, 'clear'):
            # QListWidget has clear() method
            list_widget.clear()
        else:
            # QListView doesn't have clear(), use model instead
            model = list_widget.model()
            if model:
                model.clear()
        
        UISettings.configure_list_widget(list_widget, context)
        print(f"Refreshed list widget with context '{context}': {list_widget.iconSize().width()}x{list_widget.iconSize().height()}")
    
    def add_variable_to_list(self, list_widget, var_info, icon=None):
        """Add a variable to list with formatted text and optional icon"""
        var_text = f"{var_info['label']} (ID: {var_info['id']}, Network: {var_info['network']})"
        
        # Use variable-specific PNG icon if available, otherwise default icon
        if icon is None:
            # Try to get the actual variable PNG icon from ontology_container (which IS the exchange_board)
            if hasattr(self, 'ontology_container') and self.ontology_container:
                var_id = var_info['id']
                
                # Check if ontology_container has variable icons loaded (it IS the exchange_board)
                if hasattr(self.ontology_container, 'variable_icons'):
                    if var_id in self.ontology_container.variable_icons:
                        icon = self.ontology_container.variable_icons[var_id]
                    else:
                        # Fallback to generic variable icon
                        icon = getIcon("dependent_variable")
                else:
                    # Fallback to generic variable icon if no variable_icons
                    icon = getIcon("dependent_variable")
            else:
                # Fallback to generic variable icon if no ontology_container
                icon = getIcon("dependent_variable")
        
        self.add_to_list(list_widget, var_text, icon, context='entity_variables')

    def add_port_to_list(self, list_widget, port_info, port_type="input"):
        """Add a port (input/output) to list with appropriate icon"""
        port_text = f"{port_info['label']} (ID: {port_info['id']})"
        # Use appropriate icon based on port type
        icon = getIcon("port")  # Using port icon for both input and output
        self.add_to_list(list_widget, port_text, icon)
    
    def set_entity_object(self, entity):
        """Set the Entity object and update the UI"""
        self.current_entity = entity
        print(f"EntityEditorFrontEnd received Entity object: {entity.entity_name}")
        
        # Update the lists with Entity information
        self.populate_lists_from_entity(entity)
    
    def populate_lists_from_entity(self, entity):
        """Populate the list widgets with data from the Entity object"""
        try:
            # Clear existing lists and refresh their settings
            self.clear_all_lists()
            
            # Refresh list widget settings with latest sizes
            self.refresh_list_widget_settings(self.ui.list_outputs, 'entity_variables')
            self.refresh_list_widget_settings(self.ui.list_inputs, 'entity_variables')
            self.refresh_list_widget_settings(self.ui.list_instantiate, 'entity_variables')
            self.refresh_list_widget_settings(self.ui.list_equations, 'entity_equations')
            self.refresh_list_widget_settings(self.ui.list_integrators, 'entity_variables')
            
            # Get ontology container for variable information
            ontology_container = getattr(self, 'ontology_container', None)
            if not ontology_container:
                print("Warning: No ontology container available for variable information")
                return
            
            variables = ontology_container.variables
            
            # Populate output variables list
            if hasattr(entity, 'output_vars') and entity.output_vars:
                print(f"Populating output variables: {entity.output_vars}")
                for var_id in entity.output_vars:
                    if var_id in variables:
                        var_data = variables[var_id]
                        var_info = {
                            'id': var_id,
                            'label': var_data.get('label', var_id),
                            'network': var_data.get('network', 'unknown')
                        }
                        self.add_variable_to_list(self.ui.list_outputs, var_info)
            
            # Populate input variables list
            if hasattr(entity, 'input_vars') and entity.input_vars:
                print(f"Populating input variables: {entity.input_vars}")
                for var_id in entity.input_vars:
                    if var_id in variables:
                        var_data = variables[var_id]
                        var_info = {
                            'id': var_id,
                            'label': var_data.get('label', var_id),
                            'network': var_data.get('network', 'unknown')
                        }
                        self.add_variable_to_list(self.ui.list_inputs, var_info)
            
            # Populate initialization variables list
            if hasattr(entity, 'init_vars') and entity.init_vars:
                print(f"Populating initialization variables: {entity.init_vars}")
                for var_id in entity.init_vars:
                    if var_id in variables:
                        var_data = variables[var_id]
                        var_info = {
                            'id': var_id,
                            'label': var_data.get('label', var_id),
                            'network': var_data.get('network', 'unknown')
                        }
                        self.add_variable_to_list(self.ui.list_instantiate, var_info)
            
            # Populate integrators list
            if hasattr(entity, 'integrators') and entity.integrators:
                print(f"Populating integrators: {entity.integrators}")
                for var_id, eq_id in entity.integrators.items():
                    if var_id in variables:
                        var_data = variables[var_id]
                        var_info = {
                            'id': var_id,
                            'label': var_data.get('label', var_id),
                            'network': var_data.get('network', 'unknown')
                        }
                        # Add integrator info to the text
                        var_info['label'] = f"{var_info['label']} -> {eq_id}"
                        self.add_variable_to_list(self.ui.list_integrators, var_info)
            
            # Populate equations list from var_eq_forest
            if hasattr(entity, 'var_eq_forest') and entity.var_eq_forest:
                print(f"Populating equations from var_eq_forest: {entity.var_eq_forest}")
                equations_in_forest = set()
                for tree in entity.var_eq_forest:
                    for key, values in tree.items():
                        if key.startswith('E_'):  # It's an equation
                            equations_in_forest.add(key)
                        elif values:  # It's a variable with equations
                            for eq_id in values:
                                equations_in_forest.add(eq_id)
                
                # Add equations to list
                for eq_id in equations_in_forest:
                    eq_text = f"Equation {eq_id}"
                    # Try to get equation icon from ontology_container (which IS the exchange_board)
                    icon = None
                    if hasattr(ontology_container, 'equation_icons') and eq_id in ontology_container.equation_icons:
                        icon = ontology_container.equation_icons[eq_id]
                    
                    self.add_to_list(self.ui.list_equations, eq_text, icon, context='entity_equations')
            
            # Populate undefined variables list (variables in var_eq_forest but not in defined lists)
            if hasattr(entity, 'var_eq_forest') and entity.var_eq_forest:
                print(f"Populating undefined variables from var_eq_forest")
                
                # Collect all variables that appear in the var_eq_forest
                variables_in_forest = set()
                for tree in entity.var_eq_forest:
                    for key, values in tree.items():
                        if key.startswith('V_'):  # It's a variable
                            variables_in_forest.add(key)
                        elif values:  # It's an equation with connected variables
                            for var_id in values:
                                if var_id.startswith('V_'):  # It's a variable
                                    variables_in_forest.add(var_id)
                
                # Variables that are in the forest but not explicitly defined
                defined_vars = set()
                if hasattr(entity, 'output_vars'):
                    defined_vars.update(entity.output_vars)
                if hasattr(entity, 'input_vars'):
                    defined_vars.update(entity.input_vars)
                if hasattr(entity, 'init_vars'):
                    defined_vars.update(entity.init_vars)
                
                # Undefined variables = variables in forest - defined variables
                undefined_vars = variables_in_forest - defined_vars
                
                print(f"Variables in forest: {sorted(variables_in_forest)}")
                print(f"Defined variables: {sorted(defined_vars)}")
                print(f"Undefined variables: {sorted(undefined_vars)}")
                
                # Populate undefined variables list
                for var_id in sorted(undefined_vars):
                    if var_id in variables:
                        var_data = variables[var_id]
                        var_info = {
                            'id': var_id,
                            'label': var_data.get('label', var_id),
                            'network': var_data.get('network', 'unknown')
                        }
                        self.add_variable_to_list(self.ui.list_not_defined_variables, var_info)
            
            print(f"Successfully populated lists for entity: {entity.entity_name}")
            
        except Exception as e:
            print(f"Error populating lists from Entity: {e}")
            makeMessageBox(f"Error updating entity lists: {str(e)}")
    
    def process_entity_update(self, data):
        """Process entity update message from backend"""
        try:
            print(f"EntityEditorFrontEnd processing entity update: {data}")
            
            # If we have a current entity object, update it
            if hasattr(self, 'current_entity') and self.current_entity:
                # Update the current entity with new data
                entity = self.current_entity
                
                # Update entity attributes
                if 'var_eq_forest' in data:
                    entity.var_eq_forest = data['var_eq_forest']
                if 'output_vars' in data:
                    entity.output_vars = data['output_vars']
                if 'input_vars' in data:
                    entity.input_vars = data['input_vars']
                if 'init_vars' in data:
                    entity.init_vars = data['init_vars']
                if 'integrators' in data:
                    entity.integrators = data['integrators']
                
                # Repopulate the lists
                self.populate_lists_from_entity(entity)
                
                print(f"Successfully updated entity: {entity.entity_name}")
            else:
                print("No current entity to update")
                
        except Exception as e:
            print(f"Error processing entity update: {e}")
            makeMessageBox(f"Error updating entity: {str(e)}")

    def add_integrator_to_list(self, list_widget, integrator_info):
        """Add an integrator to list with appropriate icon"""
        integrator_text = f"{integrator_info['label']} (ID: {integrator_info['id']})"
        # Using variable icon for integrators (could use a different icon if available)
        icon = getIcon("dependent_variable")
        self.add_to_list(list_widget, integrator_text, icon)

    def on_pushAddVariable_pressed(self):
        """Request behavior association editor launch from backend"""
        if not hasattr(self, 'ontology_container'):
            makeMessageBox("Ontology container not set")
            return
        
        # Send request to backend to launch association editor
        message = {
            "event": "launch_behavior_association_editor",
            "ontology_container": self.ontology_container
        }
        self.message.emit(message)  # send to entity_back_end

# ======================= window controls ==========================



    def mousePressEvent(self, event, QMouseEvent=None):
        self.dragPos = event.globalPos()

    def mouseMoveEvent(self, event, QMouseEvent=None):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()

    def markChanged(self):
        global changed
        changed = True
        self.signalButton.changeIcon("LED_red")
        self.status_label.setText("modified")

    def markSaved(self):
        global changed
        changed = False
        self.signalButton.changeIcon("LED_green")
        self.status_label.setText("up to date")

    def closeMe(self):

        if self.changed:
            dialog = makeMessageBox(message="save changes", buttons=["YES", "NO"])
            if dialog == "YES":
                self.on_pushOntologySave_pressed()
            elif dialog == "NO":
                pass
        else:
            pass
        sys.exit()