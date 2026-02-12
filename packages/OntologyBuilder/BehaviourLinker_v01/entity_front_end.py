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

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QStandardItem
from PyQt5.QtGui import QStandardItemModel

from Common.resources_icons import getIcon
from Common.resources_icons import roundButton
from OntologyBuilder.BehaviourLinker_v01.UIs.entity_changes import Ui_entity_changes
from OntologyBuilder.BehaviourLinker_v01.entity_automaton import gui_automaton
from OntologyBuilder.BehaviourLinker_v01.resources.pop_up_message_box import makeMessageBox
from OntologyBuilder.BehaviourLinker_v01.ui_settings import UISettings


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
        roundButton(self.ui.pushAddStateVariable, "dependent_variable", tooltip="add state variable")
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
        
        # Connect list widget click handlers
        self.ui.list_not_defined_variables.clicked.connect(self.on_list_pending_variables_clicked)
        
        # Connect button handlers
        self.ui.pushAccept.clicked.connect(self.on_pushAccept_pressed)
        self.ui.pushCancle.clicked.connect(self.on_pushCancle_pressed)
        self.ui.pushAddStateVariable.clicked.connect(self.on_pushAddStateVariable_pressed)
        self.ui.pushAddVariable.clicked.connect(self.on_pushAddVariable_pressed)
        
        self.mode = "load"
        self.ontology_container = None
        self.selected_entity_type = None
        self.current_entity_data = None
        global changed
        changed = False

    def interfaceComponents(self):
        self.gui_objects = {
                "buttons"  : {
                        "accept"            : self.ui.pushAccept,
                        "add_state_variable": self.ui.pushAddStateVariable,
                        "add_variable"      : self.ui.pushAddVariable,
                        "cancel"            : self.ui.pushCancle,
                        "delete_entity"     : self.ui.pushDeleteEntity,
                        "delete_variable"   : self.ui.pushDeleteVariable,
                        "edit_variable"     : self.ui.pushEditVariable,
                        },
                "indicator": {
                        "LED": self.ui.LED,
                        },
                "lists"    : {
                        "list_defined_variables"    : self.ui.list_not_defined_variables,
                        "list_pending_variables": self.ui.list_not_defined_variables,
                        "list_equations"            : self.ui.list_equations,
                        "list_integrators"          : self.ui.list_integrators,
                        "list_input"                : self.ui.list_inputs,
                        "list_output"               : self.ui.list_outputs,
                        "list_instantiate"          : self.ui.list_instantiate,
                        # "list_pending"    : self.ui.list_pending,
                        },
                }
        # pass  # OBSOLETE: Empty statement - can be removed

    def set_ontology_container(self, ontology_container):
        """Set the ontology container for behavior association"""
        self.ontology_container = ontology_container

    def update_accept_button_visibility(self):
        """Update Accept button visibility based on entity content"""
        has_content = False
        
        # Check if entity has content (variables, equations, etc.)
        if hasattr(self, 'current_entity') and self.current_entity:
            # Check if entity has any defined variables or equations
            if (hasattr(self.current_entity, 'output_vars') and self.current_entity.output_vars) or \
               (hasattr(self.current_entity, 'input_vars') and self.current_entity.input_vars) or \
               (hasattr(self.current_entity, 'init_vars') and self.current_entity.init_vars) or \
               (hasattr(self.current_entity, 'var_eq_forest') and self.current_entity.var_eq_forest):
                has_content = True
        elif hasattr(self, 'current_entity_data') and self.current_entity_data:
            # Check entity_data for content
            if (self.current_entity_data.get('defined_variables') or 
                self.current_entity_data.get('output_vars') or
                self.current_entity_data.get('input_vars') or
                self.current_entity_data.get('init_vars')):
                has_content = True
        
        # Show Accept button if entity has content
        if has_content:
            self.gui_objects["buttons"]["accept"].show()
            print("Showing Accept button - entity has content")
        else:
            self.gui_objects["buttons"]["accept"].hide()
            print("Hiding Accept button - entity is empty")

    def set_mode(self, mode):
        """Set the current mode (create, edit, load) and configure UI accordingly"""
        self.mode = mode
        print(f"EntityEditorFrontEnd mode set to: {mode}")

        # Configure button visibility based on mode
        for button_name in gui_automaton[mode]:
            self.gui_objects["buttons"][button_name].setVisible(gui_automaton[mode][button_name])

        # Update status label based on mode
        if mode == "create":
            self.status_label.setText("Create mode - Select state variable to begin")
            self.status_label.setStyleSheet("QLabel { color: blue; font-weight: bold; margin: 5px; }")
        elif mode == "edit":
            self.status_label.setText("Edit mode - Add variables to entity")
            self.status_label.setStyleSheet("QLabel { color: orange; font-weight: bold; margin: 5px; }")
        elif mode == "load":
            self.status_label.setText("Ready")
            self.status_label.setStyleSheet("QLabel { color: gray; font-style: italic; margin: 5px; }")

    def configure_buttons_for_mode(self, mode):
        """Configure button visibility based on the current mode"""
        if mode == "create":
            # In create mode: only show add state variable and cancel buttons
            self.ui.pushAddStateVariable.show()
            self.ui.pushCancle.show()

            # Hide other buttons
            self.ui.pushAddVariable.hide()
            self.ui.pushEditVariable.hide()
            self.ui.pushDeleteVariable.hide()
            self.ui.pushDeleteEntity.hide()
            self.ui.pushAccept.hide()

        elif mode == "edit":
            # In edit mode: show all relevant buttons
            self.ui.pushAddVariable.show()
            self.ui.pushEditVariable.show()
            self.ui.pushDeleteVariable.show()
            self.ui.pushAccept.show()
            self.ui.pushCancle.show()

            # Hide create-specific buttons
            self.ui.pushAddStateVariable.hide()
            self.ui.pushDeleteEntity.hide()

        elif mode == "load":
            # In load mode: show minimal buttons until selection is made
            self.ui.pushCancle.show()

            # Hide all other buttons initially
            self.ui.pushAddVariable.hide()
            self.ui.pushAddStateVariable.hide()
            self.ui.pushEditVariable.hide()
            self.ui.pushDeleteVariable.hide()
            self.ui.pushDeleteEntity.hide()
            self.ui.pushAccept.hide()

    # OBSOLETE: TODO: we may not need this one.
    # def set_selected_entity_type(self, entity_type_data):  # TODO: we may not need this one.
    #     """Set the selected entity type from the main tree"""
    #     self.selected_entity_type = entity_type_data
    #     print(f"EntityEditorFrontEnd received selected entity type: {self.selected_entity_type}")
    # 
    #     # Update the UI to show the selected entity type
    #     if self.selected_entity_type:
    #         network = self.selected_entity_type.get("network")
    #         category = self.selected_entity_type.get("category")
    #         entity_type = self.selected_entity_type.get("entity type")
    #         name = self.selected_entity_type.get("name")  # This will be None for entity types, filled for instances
    # 
    #         if name:
    #             # An entity instance was selected - we're in edit mode
    #             selection_text = f"Editing: {network}.{category}.{entity_type}.{name}"
    #             self.status_label.setText(selection_text)
    #             self.status_label.setStyleSheet("QLabel { color: orange; font-weight: bold; margin: 5px; }")
    #             self.set_mode("edit")
    #             self.load_entity_data_for_editing()
    #         else:
    #             # An entity type was selected - we're in create mode
    #             selection_text = f"Creating: {network}.{category}.{entity_type}"
    #             self.status_label.setText(selection_text)
    #             self.status_label.setStyleSheet("QLabel { color: blue; font-weight: bold; margin: 5px; }")
    #             self.set_mode("create")

    def populate_entity_structure(self, entity_data):
        """Populate entity editor with the complete entity structure from class definition"""
        try:
            print(f"=== POPULATE_ENTITY_STRUCTURE CALLED ===")
            print(f"Entity data: {entity_data}")

            # Store entity data for later use
            self.current_entity_data = entity_data

            # Check if we have an entity_object in the data
            if 'entity_object' in entity_data:
                print("Found entity_object in populate_entity_structure - using complete entity display")
                entity = entity_data['entity_object']
                self.current_entity = entity
                # Use the complete entity population method
                self.populate_lists_from_entity(entity)
            else:
                print("No entity_object found - using basic structure display")
                # Clear all lists first
                self.clear_all_lists()

                # Populate pending variables list (all variables initially)
                pending = entity_data.get('pending_variables', [])
                for var_info in pending:
                    self.add_variable_to_list(self.ui.list_not_defined_variables, var_info)

                # Initially, defined variables list is empty
                defined = entity_data.get('defined_variables', [])
                for var_info in defined:
                    self.add_variable_to_list(self.ui.list_not_defined_variables, var_info)

                # Populate equations list (initially empty)
                equations = entity_data.get('equations', [])
                for eq_info in equations:
                    self.add_to_list(self.ui.list_equations, str(eq_info), getIcon("equation"))

                # Update status to show entity being created
                entity_name = entity_data.get('entity_name', 'Unknown Entity')
                self.status_label.setText(f"Creating entity: {entity_name}")
                self.status_label.setStyleSheet("QLabel { color: blue; font-weight: bold; margin: 5px; }")

            print(f"Entity structure populated successfully")

        except Exception as e:
            print(f"Error populating entity structure: {e}")
            makeMessageBox(f"Error populating entity structure: {str(e)}")

    # OBSOLETE: Deprecated method - should not be called anymore
    # def populate_with_entity_data(self, entity_data):
    #     """Populate entity editor lists with variable and equation information"""
    #     print(f"=== POPULATE_WITH_ENTITY_DATA CALLED (OLD METHOD) ===")
    #     print(f"This method should NOT be called anymore! Data: {entity_data}")
    # 
    #     # This method is deprecated - we should use update_entity_from_backend instead
    #     # But let's keep it for backward compatibility and redirect
    #     self.update_entity_from_backend(entity_data)

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

        safe_clear_list(self.ui.list_not_defined_variables)
        safe_clear_list(self.ui.list_inputs)
        safe_clear_list(self.ui.list_outputs)
        safe_clear_list(self.ui.list_equations)
        safe_clear_list(self.ui.list_integrators)
        safe_clear_list(self.ui.list_instantiate)
        safe_clear_list(self.ui.list_included_variables)

    def add_to_list(self, list_widget, text, icon=None, context='entity_lists', data=None):
        """Add an item to a list widget with optional icon and data"""
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
        
        # Add data to item if provided
        if data is not None:
            item.setData(data, QtCore.Qt.UserRole)
            
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
        print(
            f"Refreshed list widget with context '{context}': {list_widget.iconSize().width()}x{list_widget.iconSize().height()}")

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

        self.add_to_list(list_widget, var_text, icon, context='entity_variables', data=var_info)

    # def add_port_to_list(self, list_widget, port_info, port_type="input"):
    #     """Add a port (input/output) to list with appropriate icon"""
    #     port_text = f"{port_info['label']} (ID: {port_info['id']})"
    #     # Use appropriate icon based on port type
    #     icon = getIcon("port")  # Using port icon for both input and output
    #     self.add_to_list(list_widget, port_text, icon)

    def set_entity_object(self, entity):
        """Set the Entity object and update the UI"""
        self.current_entity = entity
        print(f"EntityEditorFrontEnd received Entity object: {entity.entity_id}")

        # Update the lists with Entity information
        self.populate_lists_from_entity(entity)

    def populate_lists_from_entity(self, entity):
        """Populate the list widgets with data from the Entity object"""
        try:
            print(f"=== POPULATE_LISTS_FROM_ENTITY CALLED ===")
            print(f"Entity object: {entity}")
            print(f"Entity name: {entity.entity_id}")
            print(f"Entity output_vars: {getattr(entity, 'output_vars', 'None')}")
            print(f"Entity input_vars: {getattr(entity, 'input_vars', 'None')}")
            print(f"Entity init_vars: {getattr(entity, 'init_vars', 'None')}")
            print(f"Entity integrators: {getattr(entity, 'integrators', 'None')}")
            print(f"Entity var_eq_forest: {getattr(entity, 'var_eq_forest', 'None')}")

            # Clear existing lists and refresh their settings
            self.clear_all_lists()

            # Refresh list widget settings with latest sizes
            self.refresh_list_widget_settings(self.ui.list_outputs, 'entity_variables')
            self.refresh_list_widget_settings(self.ui.list_inputs, 'entity_variables')
            self.refresh_list_widget_settings(self.ui.list_instantiate, 'entity_variables')
            self.refresh_list_widget_settings(self.ui.list_equations, 'entity_equations')
            self.refresh_list_widget_settings(self.ui.list_integrators, 'entity_variables')
            self.refresh_list_widget_settings(self.ui.list_included_variables, 'entity_variables')

            # Get ontology container for variable information
            ontology_container = getattr(self, 'ontology_container', None)
            if not ontology_container:
                print("Warning: No ontology container available for variable information")
                return

            variables = ontology_container.variables
            print(f"Available variables in ontology: {list(variables.keys())[:10]}...")  # Show first 10

            # Populate output variables list
            if hasattr(entity, 'output_vars') and entity.output_vars:
                print(f"Populating output variables: {entity.output_vars}")
                for var_id in entity.output_vars:
                    if var_id in variables:
                        var_data = variables[var_id]
                        var_info = {
                                'id'     : var_id,
                                'label'  : var_data.get('label', var_id),
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
                                'id'     : var_id,
                                'label'  : var_data.get('label', var_id),
                                'network': var_data.get('network', 'unknown')
                                }
                        self.add_variable_to_list(self.ui.list_inputs, var_info)

            # Populate included variables list (all variables in the entity)
            if hasattr(entity, 'get_all_variables'):
                all_variables = entity.get_all_variables()
                print(f"Populating all included variables: {all_variables}")
                for var_id in all_variables:
                    if var_id in variables:
                        var_data = variables[var_id]
                        var_info = {
                                'id'     : var_id,
                                'label'  : var_data.get('label', var_id),
                                'network': var_data.get('network', 'unknown')
                                }
                        self.add_variable_to_list(self.ui.list_included_variables, var_info)

            # Populate variables to be instantiated list
            if hasattr(entity, 'get_variables_to_be_instantiated'):
                vars_to_instantiate = entity.get_variables_to_be_instantiated()
                print(f"Populating variables to be instantiated: {vars_to_instantiate}")
                
                for var_id in vars_to_instantiate:
                    if var_id in variables:
                        var_data = variables[var_id]
                        var_info = {
                                'id'     : var_id,
                                'label'  : var_data.get('label', var_id),
                                'network': var_data.get('network', 'unknown')
                                }
                        self.add_variable_to_list(self.ui.list_instantiate, var_info)

            # Populate integrators list
            if hasattr(entity, 'integrators') and entity.integrators:
                print(f"=== POPULATING INTEGRATORS ===")
                print(f"Entity integrators: {entity.integrators}")
                print(f"Type of integrators: {type(entity.integrators)}")
                for var_id, eq_id in entity.integrators.items():
                    print(f"Processing integrator: {var_id} -> {eq_id}")
                    if var_id in variables:
                        var_data = variables[var_id]
                        var_info = {
                                'id'     : var_id,
                                'label'  : var_data.get('label', var_id),
                                'network': var_data.get('network', 'unknown')
                                }
                        # Add integrator info to the text
                        var_info['label'] = f"{var_info['label']} -> {eq_id}"
                        print(f"Adding integrator to list: {var_info['label']}")
                        self.add_variable_to_list(self.ui.list_integrators, var_info)
                    else:
                        print(f"Variable {var_id} not found in ontology variables")
            else:
                print("=== NO INTEGRATORS FOUND ===")
                print(f"Has integrators attribute: {hasattr(entity, 'integrators')}")
                if hasattr(entity, 'integrators'):
                    print(f"Integrators value: {entity.integrators}")
                    print(f"Integrators type: {type(entity.integrators)}")
                    print(f"Integrators truthiness: {bool(entity.integrators)}")

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

            # Populate pending variables using Entity method
            if hasattr(entity, 'get_pending_vars'):
                pending_vars = entity.get_pending_vars()
                print(f"Populating pending variables from Entity method: {pending_vars}")
                
                for var_id in pending_vars:
                    if var_id in variables:
                        var_data = variables[var_id]
                        var_info = {
                                'id'     : var_id,
                                'label'  : var_data.get('label', var_id),
                                'network': var_data.get('network', 'unknown')
                                }
                        self.add_variable_to_list(self.ui.list_not_defined_variables, var_info)

            print(f"Successfully populated lists for entity: {entity.entity_id}")

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

                print(f"Successfully updated entity: {entity.entity_id}")
            else:
                print("No current entity to update")

        except Exception as e:
            print(f"Error processing entity update: {e}")
            makeMessageBox(f"Error updating entity: {str(e)}")

    def on_pushAddStateVariable_pressed(self):
        """Handle add state variable button for create mode"""
        # entity_id = self.current_entity_data["entity_id"]
        message = {"event": "add_state_variable"}  # , "entity_id": entity_id}
        self.message.emit(message)

    def on_pushAddVariable_pressed(self):
        """Handle add variable button - opens equation selection for any selected variable"""
        message = {"event": "add_variable"}
        self.message.emit(message)
        self.ui.list_not_defined_variables

    def on_pushAccept_pressed(self):
        """Handle Accept button - save entity and close"""
        try:
            print("Accept button pressed - saving entity")
            
            # Mark entity as saved
            self.markSaved()
            
            # Send save message to backend
            if hasattr(self, 'current_entity') and self.current_entity:
                message = {
                    "event": "save_entity",
                    "entity": self.current_entity
                }
                self.message.emit(message)
                print(f"Sent save_entity message: {message}")
                self.close()
            else:
                print("No entity to save")
                
        except Exception as e:
            print(f"Error in accept handler: {e}")
            makeMessageBox(f"Error saving entity: {str(e)}")

    def on_pushCancle_pressed(self):
        """Handle Cancel button - close without saving"""
        global changed
        try:
            # print("Cancel button pressed - closing without saving")
            # print(f"Current changed state: {self.changed}")
            
            # Check if there are unsaved changes
            if changed:
                print("Showing save changes dialog...")
                dialog = makeMessageBox(message="save changes", buttons=["YES", "NO"])
                print(f"Dialog result: {dialog}")
                if dialog == "YES":
                    # User wants to save before canceling
                    self.on_pushAccept_pressed()
                    return
                elif dialog == "NO":
                    # User wants to discard changes
                    pass
            else:
                print("No unsaved changes detected")

            # Close the window
            self.closeMe()
                
        except Exception as e:
            print(f"Error in cancel handler: {e}")
            makeMessageBox(f"Error canceling: {str(e)}")

    def on_list_pending_variables_clicked(self, index):
        """Handle click on pending variables list - go directly to equation selection"""
        
        print(">>>>>>>>>>>>>>>>>>>>>>>")
        print(f"Clicked index: {index}")
        
        # Get the model and item from the index
        model = self.ui.list_not_defined_variables.model()
        if model and index.isValid():
            item = model.itemFromIndex(index)
            if item:
                # Get the text and data from the clicked item
                item_text = item.text()
                item_data = item.data(QtCore.Qt.UserRole)
                
                print(f"Item text: {item_text}")
                print(f"Item data: {item_data}")
                
                # Extract variable ID from the item text
                # Format is typically: "label (ID: var_id, Network: network)"
                var_id = item_data.get('id')
                var_label = item_data.get('label')
                var_network = item_data.get('network')
                print(f"Variable ID: {var_id}")
                print(f"Variable Label: {var_label}")
                print(f"Variable Network: {var_network}")
                
                # Go directly to equation association editor for this variable
                message = {
                    "event": "def_variable", 
                    "var_id": var_id, 
                    "var_label": var_label, 
                    "var_network": var_network
                }
                self.message.emit(message)


    def launch_state_variable_selector(self):
        """Launch state variable selector for create mode"""
        try:
            from OntologyBuilder.BehaviourLinker_v01.behaviour_association.editor import \
                launch_behavior_association_editor

            # Get entity type information for rule-based filtering
            entity_type_info = {
                    'network'    : self.selected_entity_type.get('network',
                                                                 'unknown') if self.selected_entity_type else 'unknown',
                    'category'   : self.selected_entity_type.get('category',
                                                                 'unknown') if self.selected_entity_type else 'unknown',
                    'entity type': self.selected_entity_type.get('entity type',
                                                                 'unknown') if self.selected_entity_type else 'unknown'
                    }

            print(f"Create mode: Launching state variable selector for entity type: {entity_type_info}")

            # Launch the BehaviorAssociation editor in state variable selection mode
            assignments = launch_behavior_association_editor(self.ontology_container, entity_type_info)

            if assignments:
                # Process the state variable selection
                self.handle_state_variable_selection(assignments)
            else:
                print("No state variable selected")

        except Exception as e:
            print(f"Error launching state variable selector: {e}")
            makeMessageBox(f"Error launching state variable selector: {str(e)}")

    def launch_new_variable_selector(self):
        """Launch new variable selector for edit mode"""
        try:
            from OntologyBuilder.BehaviourLinker_v01.behaviour_association.editor import \
                launch_behavior_association_editor

            # Get current entity information
            entity_type_info = {
                    'network'    : self.selected_entity_type.get('network',
                                                                 'unknown') if self.selected_entity_type else 'unknown',
                    'category'   : self.selected_entity_type.get('category',
                                                                 'unknown') if self.selected_entity_type else 'unknown',
                    'entity type': self.selected_entity_type.get('entity type',
                                                                 'unknown') if self.selected_entity_type else 'unknown',
                    'entity_name': self.selected_entity_type.get('name',
                                                                 'unknown') if self.selected_entity_type else 'unknown'
                    }

            print(f"Edit mode: Launching new variable selector for entity: {entity_type_info}")

            # Launch the BehaviorAssociation editor in new variable addition mode
            assignments = launch_behavior_association_editor(self.ontology_container, entity_type_info)

            if assignments:
                # Process the new variable addition
                self.handle_new_variable_addition(assignments)
            else:
                print("No new variable added")

        except Exception as e:
            print(f"Error launching new variable selector: {e}")
            makeMessageBox(f"Error launching new variable selector: {str(e)}")

    def launch_behavior_association_editor(self):
        """Original behavior association editor launch"""
        # Send request to backend to launch association editor
        message = {
                "event"             : "launch_behavior_association_editor",
                "ontology_container": self.ontology_container
                }
        self.message.emit(message)  # send to entity_back_end

    def handle_state_variable_selection(self, assignments):
        """Handle state variable selection in create mode"""
        try:
            print(f"State variable selected: {assignments}")

            # Extract the selected variable
            root_variable = assignments.get('root_variable')
            if root_variable:
                # Move to edit mode after state selection
                self.mode = "edit"
                self.configure_buttons_for_mode("edit")  # Update button visibility
                self.status_label.setText(f"State variable selected: {root_variable}. Now in edit mode.")
                self.status_label.setStyleSheet("QLabel { color: orange; font-weight: bold; margin: 5px; }")

                # Note: All variable list management is handled by Entity class in back end
                # Front end only triggers backend processing and displays Entity results

                # Send to backend for processing - use Entity object data if available
                entity_data = self.current_entity_data.copy() if self.current_entity_data else {}
                if hasattr(self, 'current_entity') and self.current_entity:
                    # Update entity_data with current Entity object state
                    entity_data.update({
                        'entity_object': self.current_entity,
                        'entity_id': getattr(self.current_entity, 'entity_id', ''),
                        'var_eq_forest': getattr(self.current_entity, 'var_eq_forest', []),
                        'output_vars': getattr(self.current_entity, 'output_vars', []),
                        'input_vars': getattr(self.current_entity, 'input_vars', []),
                        'init_vars': getattr(self.current_entity, 'init_vars', []),
                        'integrators': getattr(self.current_entity, 'integrators', {})
                    })

                message = {
                        "event"      : "state_variable_selected",
                        "assignments": assignments,
                        "entity_data": entity_data
                        }
                self.message.emit(message)
            else:
                makeMessageBox("No valid state variable selected")

        except Exception as e:
            print(f"Error handling state variable selection: {e}")
            makeMessageBox(f"Error handling state variable selection: {str(e)}")

    def handle_new_variable_addition(self, assignments):
        """Handle new variable addition in edit mode"""
        try:
            print(f"New variable added: {assignments}")

            # Extract the new variable information
            root_variable = assignments.get('root_variable')
            if root_variable:
                # Note: Variable list management is handled by Entity class in back end
                # Front end only triggers backend processing and displays results
                if hasattr(self, 'current_entity') and self.current_entity:
                    # Update status
                    self.status_label.setText(f"New variable '{assignments.get('variable_label', root_variable)}' added to entity")
                    self.status_label.setStyleSheet("QLabel { color: green; font-weight: bold; margin: 5px; }")

                # Send to backend for processing - use Entity object data if available
                entity_data = self.current_entity_data.copy() if self.current_entity_data else {}
                if hasattr(self, 'current_entity') and self.current_entity:
                    # Update entity_data with current Entity object state
                    entity_data.update({
                        'entity_object': self.current_entity,
                        'entity_id': getattr(self.current_entity, 'entity_id', ''),
                        'var_eq_forest': getattr(self.current_entity, 'var_eq_forest', []),
                        'output_vars': getattr(self.current_entity, 'output_vars', []),
                        'input_vars': getattr(self.current_entity, 'input_vars', []),
                        'init_vars': getattr(self.current_entity, 'init_vars', []),
                        'integrators': getattr(self.current_entity, 'integrators', {})
                    })

                message = {
                        "event"      : "new_variable_added",
                        "assignments": assignments,
                        "entity_data": entity_data
                        }
                self.message.emit(message)
            else:
                makeMessageBox("No valid new variable provided")

        except Exception as e:
            print(f"Error handling new variable addition: {e}")
            makeMessageBox(f"Error handling new variable addition: {str(e)}")

    def update_entity_from_backend_entity(self, entity):
        """Update display when backend sends Entity object - Entity-only approach"""
        try:
            print(f"=== UPDATE_ENTITY_FROM_BACKEND_ENTITY CALLED ===")
            print(f"Entity object: {entity}")
            print(f"Entity var_eq_forest: {getattr(entity, 'var_eq_forest', 'None')}")
            print(f"Entity output_vars: {getattr(entity, 'output_vars', 'None')}")
            print(f"Entity input_vars: {getattr(entity, 'input_vars', 'None')}")
            print(f"Entity init_vars: {getattr(entity, 'init_vars', 'None')}")
            
            # Store current entity
            self.current_entity = entity
            
            # Use Entity methods directly for all lists
            self.populate_lists_from_entity(entity)
            
            # Update Accept button visibility based on entity content
            self.update_accept_button_visibility()
                
        except Exception as e:
            print(f"Error updating entity display: {e}")
            makeMessageBox(f"Error updating entity display: {str(e)}")

    def update_entity_from_backend_new(self, entity_data):
        """Deprecated - redirect to Entity-only approach"""
        # Extract Entity object from entity_data
        if 'entity_object' in entity_data and entity_data['entity_object']:
            self.update_entity_from_backend_entity(entity_data['entity_object'])
        else:
            print("No Entity object in entity_data - cannot update display")
        """Update entity display when backend sends updated entity data"""
        try:
            print(f"=== UPDATE_ENTITY_FROM_BACKEND CALLED ===")
            print(f"Updating entity display from backend: {entity_data}")

            # Check if we have an entity object in the data
            if 'entity_object' in entity_data:
                print("Found entity_object in data - using populate_lists_from_entity")
                entity = entity_data['entity_object']
                self.current_entity = entity
                # Use the complete entity population method
                self.populate_lists_from_entity(entity)
            else:
                print("No entity_object found - using fallback method")
                # Fallback to current_entity_data if no entity object
                self.populate_from_entity_data_fallback(entity_data)

            print("Entity display updated successfully")

        except Exception as e:
            print(f"Error updating entity display: {e}")
            makeMessageBox(f"Error updating entity display: {str(e)}")

    def populate_from_entity_data_fallback(self, entity_data):
        """Fallback method to populate lists when no Entity object is available - all list management should be done by Entity class"""
        try:
            # Clear all lists
            self.clear_all_lists()
            
            # Show status message - all list management should be done by Entity class
            self.status_label.setText("No Entity object available - pending variable management must be done by Entity class")
            self.status_label.setStyleSheet("QLabel { color: orange; font-weight: bold; margin: 5px; }")

            # Note: All list management should be done by Entity class methods
            # Manual list population removed from fallback method

            # All remaining manual list management removed - Entity class should handle all lists

            # If Entity object is available, use the proper Entity-based method
            if hasattr(self, 'current_entity') and self.current_entity:
                entity = self.current_entity
                self.populate_lists_from_entity(entity)  # Use Entity methods for all list management
        except:
            print("error in populate_from_entity_data_fallback ")

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

        if changed:
            dialog = makeMessageBox(message="loose changes", buttons=["YES", "NO"])
            if dialog == "YES":
                return
            elif dialog == "NO":
                pass  # OBSOLETE: Empty else clause - can be removed
        else:
            pass  # OBSOLETE: Empty else clause - can be removed
        self.close()
