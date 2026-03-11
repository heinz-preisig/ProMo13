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


# Error logging utility
def log_error(method_name: str, error: Exception, context: str = ""):
    """Log error with method name and context for debugging"""
    error_msg = f"ERROR in {method_name}"
    if context:
        error_msg += f" ({context})"
    error_msg += f": {str(error)}"
    print(error_msg)  # Keep console output for debugging
    # Could also write to a log file here if needed


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
        roundButton(self.ui.pushAddTransport, "token_flow", tooltip="add transport variable")
        roundButton(self.ui.pushEditVariable, "edit", tooltip="edit variable")
        roundButton(self.ui.pushDeleteVariable, "delete", tooltip="delete variable")
        roundButton(self.ui.pushAccept, "accept", tooltip="accept")
        roundButton(self.ui.pushCancle, "cancel", tooltip="cancel")
        roundButton(self.ui.pushAddIntensitity, "infinity", tooltip="secondary states -- intensities")
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
        self.ui.list_not_defined_variables.doubleClicked.connect(self.on_list_pending_variables_double_clicked)
        self.ui.list_not_defined_variables.clicked.connect(self.on_list_pending_variables_single_clicked)
        
        # Connect single-click handlers for other lists to open classification selector
        self.ui.list_inputs.clicked.connect(self.on_list_pending_variables_single_clicked)
        self.ui.list_outputs.clicked.connect(self.on_list_pending_variables_single_clicked)
        self.ui.list_instantiate.clicked.connect(self.on_list_pending_variables_single_clicked)
        
        # Connect other lists only for delete button management (not inputs/outputs/instantiate since they use classification selector)
        self.ui.list_integrators.clicked.connect(self.on_list_item_clicked)
        self.ui.list_included_variables.clicked.connect(self.on_list_item_clicked)

        # Connect selection change handlers for proper delete button management
        # Defer this until lists are properly initialized
        self._setup_selection_handlers()

        # Connect button handlers
        self.ui.pushAccept.clicked.connect(self.on_pushAccept_pressed)
        self.ui.pushCancle.clicked.connect(self.on_pushCancle_pressed)
        self.ui.pushAddStateVariable.clicked.connect(self.on_pushAddStateVariable_pressed)
        self.ui.pushAddTransport.clicked.connect(self.on_pushAddTransport_pressed)
        self.ui.pushAddVariable.clicked.connect(self.on_pushAddVariable_pressed)
        self.ui.pushAddIntensitity.clicked.connect(self.on_pushAddIntensitity_pressed)
        self.ui.pushDeleteVariable.clicked.connect(self.on_pushDeleteVariable_pressed)

        self.mode = "load"
        self.ontology_container = None
        self.selected_entity_type = None
        self.current_entity_data = None
        
        # Edit mode tracking variables
        self.is_edit_mode = False
        self.original_entity_id = None
        self.original_entity = None
        
        global changed
        
        # Setup click timer for double-click detection
        from PyQt5.QtCore import QTimer
        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.handle_single_click)
        self.pending_click_data = None
        changed = False

    def _setup_selection_handlers(self):
        """Safely setup selection change handlers for all lists"""
        try:
            lists_to_setup = [
                    self.ui.list_outputs,
                    self.ui.list_inputs,
                    self.ui.list_instantiate,
                    self.ui.list_integrators,
                    self.ui.list_included_variables,
                    self.ui.list_not_defined_variables
                    ]

            for list_widget in lists_to_setup:
                try:
                    selection_model = list_widget.selectionModel()
                    if selection_model is not None:
                        selection_model.selectionChanged.connect(self.on_list_selection_changed)
                        # Connected selection handler
                    else:
                        # No selection model needed for this list
                        pass
                except Exception as e:
                    log_error("_setup_selection_handlers", e, f"setting up {list_widget.objectName()}")

        except Exception as e:
            log_error("_setup_selection_handlers", e, "main setup loop")

    def interfaceComponents(self):
        self.gui_objects = {
                "buttons"  : {
                        "accept"            : self.ui.pushAccept,
                        "add_state_variable": self.ui.pushAddStateVariable,
                        "add_transport"     : self.ui.pushAddTransport,
                        "add_variable"      : self.ui.pushAddVariable,
                        "add_intensity"     : self.ui.pushAddIntensitity,
                        "cancel"            : self.ui.pushCancle,
                        "delete_variable"   : self.ui.pushDeleteVariable,
                        "edit_variable"     : self.ui.pushEditVariable,
                        },
                "indicator": {
                        "LED": self.ui.LED,
                        },
                "lists"    : {
                        "list_defined_variables": self.ui.list_not_defined_variables,
                        "list_pending_variables": self.ui.list_not_defined_variables,
                        "list_equations"        : self.ui.list_equations,
                        "list_integrators"      : self.ui.list_integrators,
                        "list_input"            : self.ui.list_inputs,
                        "list_output"           : self.ui.list_outputs,
                        "list_instantiate"      : self.ui.list_instantiate,
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
        else:
            self.gui_objects["buttons"]["accept"].hide()

    def set_selected_entity_type(self, entity_type_data):
        """Set the selected entity type from the main tree"""
        self.selected_entity_type = entity_type_data
        print(f"EntityEditorFrontEnd received selected entity type: {self.selected_entity_type}")

    def set_mode(self, mode):
        """Set the current mode and configure UI accordingly"""
        # Determine entity-type-specific mode if we have entity type info
        if self.selected_entity_type:
            category = self.selected_entity_type.get('category', '').lower()
            entity_type = self.selected_entity_type.get('entity type', '').lower()
            
            # Check if this is a reservoir entity (contains constant|infinity)
            is_reservoir = 'constant|infinity' in entity_type
            
            if category == 'node':
                if mode == "create":
                    if is_reservoir:
                        mode = "create_reservoir"  # Use special reservoir mode
                    else:
                        mode = "create_node"
                elif mode == "edit_no_selection":
                    mode = "edit_no_selection_node"
                elif mode == "edit_with_selection":
                    mode = "edit_with_selection_node"
            elif category == 'arc':
                if mode == "create":
                    mode = "create_arc"
                elif mode == "edit_no_selection":
                    mode = "edit_no_selection_arc"
                elif mode == "edit_with_selection":
                    mode = "edit_with_selection_arc"
        
        self.mode = mode

        # Configure button visibility based on mode using automaton
        if mode in gui_automaton:
            self.__setInterface(mode)

        # Update status label based on mode
        if mode == "create_reservoir":
            self.status_label.setText("Reservoir creation mode - Use 'add intensity' for secondary states")
            self.status_label.setStyleSheet("QLabel { color: purple; font-weight: bold; margin: 5px; }")
        elif mode == "edit_reservoir":
            self.status_label.setText("Reservoir edit mode - Use 'add intensity' to add more secondary states")
            self.status_label.setStyleSheet("QLabel { color: purple; font-weight: bold; margin: 5px; }")
        elif mode == "edit_with_selection_reservoir":
            self.status_label.setText("Reservoir edit mode - Variable selected, delete enabled")
            self.status_label.setStyleSheet("QLabel { color: purple; font-weight: bold; margin: 5px; }")
        elif mode.startswith("create"):
            self.status_label.setText("Create mode - Select state variable to begin")
            self.status_label.setStyleSheet("QLabel { color: blue; font-weight: bold; margin: 5px; }")
        elif mode.startswith("edit_no_selection"):
            self.status_label.setText("Edit mode - Select a variable to delete")
            self.status_label.setStyleSheet("QLabel { color: orange; font-weight: bold; margin: 5px; }")
        elif mode.startswith("edit_with_selection"):
            self.status_label.setText("Edit mode - Variable selected, delete enabled")
            self.status_label.setStyleSheet("QLabel { color: green; font-weight: bold; margin: 5px; }")
        elif mode == "load":
            self.status_label.setText("Ready")
            self.status_label.setStyleSheet("QLabel { color: gray; font-style: italic; margin: 5px; }")

    def _update_mode_based_on_selection(self):
        """Update mode based on whether a variable is selected"""
        has_selection = self.get_selected_variable_id() is not None

        if self.mode.startswith("edit_no_selection") and has_selection:
            # Switch to mode with delete enabled
            if "node" in self.mode:
                self.set_mode("edit_with_selection_node")
            elif "arc" in self.mode:
                self.set_mode("edit_with_selection_arc")
            elif "reservoir" in self.mode:
                self.set_mode("edit_with_selection_reservoir")  # Use proper reservoir selection mode
            else:
                self.set_mode("edit_with_selection")
        elif self.mode.startswith("edit_with_selection") and not has_selection:
            # Switch to mode with delete disabled
            if "node" in self.mode:
                self.set_mode("edit_no_selection_node")
            elif "arc" in self.mode:
                self.set_mode("edit_no_selection_arc")
            elif "reservoir" in self.mode:
                self.set_mode("edit_reservoir")  # Return to reservoir edit mode when no selection
            else:
                self.set_mode("edit_no_selection")
        elif self.mode in ["create", "load"]:
            # Don't interfere with create/load modes
            pass

    def __setInterface(self, mode):
        for button_name in gui_automaton[mode]:
            self.gui_objects["buttons"][button_name].setVisible(gui_automaton[mode][button_name])

    def configure_buttons_for_mode(self, mode):
        """Configure button visibility and state based on the current mode"""
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

            # Initially disable delete button until a variable is selected
            self.ui.pushDeleteVariable.setEnabled(False)

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
            # Store entity data for later use
            self.current_entity_data = entity_data

            # Check if we have an entity_object in the data
            if 'entity_object' in entity_data:
                entity = entity_data['entity_object']
                self.current_entity = entity
                # Use the complete entity population method
                self.populate_lists_from_entity(entity)
            else:
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

            # Entity structure populated

        except Exception as e:
            log_error("populate_entity_structure", e, "populating entity data")
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

        # Update the lists with Entity information
        self.populate_lists_from_entity(entity)

    def populate_lists_from_entity(self, entity):
        """Populate the list widgets with data from the Entity object"""
        try:
            # Check if this is the first time lists are being calculated
            is_first_time = not hasattr(entity, 'classifications_initialized') or not entity.classifications_initialized
            
            # Get ontology container for variable data

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
                print(f"DEBUG: No ontology container found")
                return

            variables = ontology_container.variables

            # Build local variable classifications if this is the first time
            if is_first_time:
                entity.build_local_variable_classifications(variables)

            # Populate output variables list
            output_vars = entity.get_output_vars()
            for var_id in output_vars:
                if var_id in variables:
                    var_data = variables[var_id]
                    var_info = {
                            'id'     : var_id,
                            'label'  : var_data.get('label', var_id),
                            'network': var_data.get('network', 'unknown')
                            }
                    self.add_variable_to_list(self.ui.list_outputs, var_info)

            # Populate input variables list
            input_vars = entity.get_input_vars()
            for var_id in input_vars:
                if var_id in variables:
                    var_data = variables[var_id]
                    var_info = {
                            'id'     : var_id,
                            'label'  : var_data.get('label', var_id),
                            'network': var_data.get('network', 'unknown')
                            }
                    self.add_variable_to_list(self.ui.list_inputs, var_info)

            # Populate instantiate list
            instantiate_vars = entity.get_variables_to_be_instantiated()
            for var_id in instantiate_vars:
                if var_id in variables:
                    var_data = variables[var_id]
                    var_info = {
                            'id'     : var_id,
                            'label'  : var_data.get('label', var_id),
                            'network': var_data.get('network', 'unknown')
                            }
                    self.add_variable_to_list(self.ui.list_instantiate, var_info)

            # Populate included variables list (all variables in the entity)
            # if hasattr(entity, 'get_all_variables'):
            all_included_vars = entity.get_entity_variables()
            # all_variables = entity.get_all_variables()
            for var_id in all_included_vars:
                if var_id in variables:
                    var_data = variables[var_id]
                    var_info = {
                            'id'     : var_id,
                            'label'  : var_data.get('label', var_id),
                            'network': var_data.get('network', 'unknown')
                            }
                    self.add_variable_to_list(self.ui.list_included_variables, var_info)

            # if hasattr(entity, 'integrators') and entity.integrators:
            for var_id in entity.get_integrator_vars():
                if var_id in variables:
                    var_data = variables[var_id]
                    var_info = {
                            'id'     : var_id,
                            'label'  : var_data.get('label', var_id),
                            'network': var_data.get('network', 'unknown')
                            }
                    # Add integrator info to the text
                    # var_info['label'] = f"{var_info['label']} -> {eq_id}"
                    self.add_variable_to_list(self.ui.list_integrators, var_info)

            equations = entity.get_equations()
            for eq_id in equations:
                eq_text = f"{eq_id}"
                icon = ontology_container.equation_icons[eq_id]
                self.add_to_list(self.ui.list_equations, eq_text, icon, context='entity_equations')

            # # Populate equations list from var_eq_forest
            # if hasattr(entity, 'var_eq_forest') and entity.var_eq_forest:
            #     equations_in_forest = set()
            #     for tree in entity.var_eq_forest:
            #         for key, values in tree.items():
            #             if key.startswith('E_'):  # It's an equation
            #                 equations_in_forest.add(key)
            #             elif values:  # It's a variable with equations
            #                 for eq_id in values:
            #                     equations_in_forest.add(eq_id)
            #
            #     # Add equations to list
            #     for eq_id in equations_in_forest:
            #         eq_text = f"Equation {eq_id}"
            #         # Try to get equation icon from ontology_container (which IS the exchange_board)
            #         icon = None
            #         if hasattr(ontology_container, 'equation_icons') and eq_id in ontology_container.equation_icons:
            #             icon = ontology_container.equation_icons[eq_id]
            #
            #         self.add_to_list(self.ui.list_equations, eq_text, icon, context='entity_equations')

            # Populate pending variables using Entity method
            # if hasattr(entity, 'get_pending_vars'):
            pending_vars = entity.get_pending_vars()

            for var_id in pending_vars:
                if var_id in variables:
                    var_data = variables[var_id]
                    var_info = {
                            'id'     : var_id,
                            'label'  : var_data.get('label', var_id),
                            'network': var_data.get('network', 'unknown')
                            }
                    self.add_variable_to_list(self.ui.list_not_defined_variables, var_info)

            # Setup selection handlers now that lists are populated
            self._setup_selection_handlers()

            # Update mode based on selection after populating lists
            self._update_mode_based_on_selection()

        except Exception as e:
            log_error("populate_lists_from_entity", e, f"populating lists for {getattr(entity, 'entity_id', 'unknown entity')}")
            makeMessageBox(f"Error updating entity lists: {str(e)}")

    def process_entity_update(self, data):
        """Process entity update message from backend"""
        try:
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
            else:
                pass

        except Exception as e:
            log_error("process_entity_update", e, "processing entity update message")
            makeMessageBox(f"Error updating entity: {str(e)}")

    def on_pushAddStateVariable_pressed(self):
        """Handle add state variable button for create mode"""
        # entity_id = self.current_entity_data["entity_id"]
        message = {"event": "add_state_variable"}  # , "entity_id": entity_id}
        self.message.emit(message)

    def on_pushAddTransport_pressed(self):
        """Handle add transport variable button for arc entities"""
        message = {"event": "add_transport"}
        self.message.emit(message)

    def on_pushAddVariable_pressed(self):
        """Handle add variable button - opens equation selection for any selected variable"""
        message = {"event": "add_variable"}
        self.message.emit(message)
        # self.ui.list_not_defined_variables

    def on_pushAddIntensitity_pressed(self):
        """Handle add intensity button - used for reservoir creation (constant|infinity entities)"""
        # Use same approach as other add buttons - launch behavior association editor
        message = {"event": "add_intensity"}
        self.message.emit(message)

    
    
    def on_pushDeleteVariable_pressed(self):
        """Handle delete variable button - deletes selected variable from entity"""
        try:
            # Get the currently selected variable from any of the lists
            selected_var_id = self.get_selected_variable_id()

            if not selected_var_id:
                # No variable selected
                from OntologyBuilder.BehaviourLinker_v01.resources.pop_up_message_box import makeMessageBox
                makeMessageBox("Please select a variable to delete")
                return

            # Delete button pressed

            # Confirm deletion
            from OntologyBuilder.BehaviourLinker_v01.resources.pop_up_message_box import makeMessageBox
            result = makeMessageBox(f"Delete variable {selected_var_id} from entity?", buttons=["YES", "NO"])

            if result == "YES":
                # Send delete message to backend
                message = {
                        "event" : "delete_variable",
                        "var_id": selected_var_id
                        }
                self.message.emit(message)
            else:
                pass

        except Exception as e:
            log_error("on_pushDeleteVariable_pressed", e, f"deleting variable {selected_var_id}")
            from OntologyBuilder.BehaviourLinker_v01.resources.pop_up_message_box import makeMessageBox
            makeMessageBox(f"Error deleting variable: {str(e)}")

    def get_selected_variable_id(self):
        """Get the ID of the currently selected variable from any list"""
        try:
            # Check all relevant lists for selected items
            lists_to_check = [
                    self.ui.list_outputs,
                    self.ui.list_inputs,
                    self.ui.list_instantiate,
                    self.ui.list_integrators,
                    self.ui.list_included_variables
                    ]

            for list_widget in lists_to_check:
                # Checking list

                # QListView uses selectionModel() instead of selectedItems()
                selection_model = list_widget.selectionModel()
                if selection_model:
                    selected_indexes = selection_model.selectedIndexes()
                    # Found selected indexes

                    if selected_indexes:
                        # Get the first selected index
                        selected_index = selected_indexes[0]
                        model = list_widget.model()

                        if model:
                            item = model.itemFromIndex(selected_index)
                            if item:
                                # Selected item

                                item_data = item.data(QtCore.Qt.UserRole)
                                # Got item data

                                if item_data and 'id' in item_data:
                                    return item_data['id']

                                # Try to extract ID from text if no data
                                item_text = item.text()
                                import re
                                match = re.search(r'ID:\s*(\w+)', item_text)
                                if match:
                                    return match.group(1)
                else:
                    # No selection model
                    pass

            # No selected variable found
            return None

        except Exception as e:
            log_error("get_selected_variable_id", e, "getting selected variable")
            return None

    def on_list_item_clicked(self, index):
        """Handle item click in any variable list"""
        try:
            list_widget = self.sender()

            # Update mode based on selection
            self._update_mode_based_on_selection()

        except Exception as e:
            pass

    def on_list_selection_changed(self, selected, deselected):
        """Handle selection change in any variable list"""
        try:
            # Update mode based on selection
            self._update_mode_based_on_selection()

        except Exception as e:
            pass

    def on_pushAccept_pressed(self):
        """Handle Accept button - save entity and close"""
        try:
            # Mark entity as saved
            self.markSaved()

            # Send save message to backend
            if hasattr(self, 'current_entity') and self.current_entity:
                message = {
                        "event" : "save_entity",
                        "entity": self.current_entity
                        }
                self.message.emit(message)
                self.close()
            else:
                pass

        except Exception as e:
            log_error("on_pushAccept_pressed", e, "saving entity")
            makeMessageBox(f"Error saving entity: {str(e)}")

    def on_pushCancle_pressed(self):
        """Handle Cancel button - close without saving, discarding all changes
        
        In edit mode, this discards the copy and preserves the original entity unchanged.
        In create mode, this discards the new entity being created.
        """
        global changed
        try:
            # Reset the changed flag without prompting
            changed = False
            self.markSaved()  # Update UI to show saved state

            # Close the window immediately
            # The copy (if in edit mode) or new entity (if in create mode) is discarded
            self.closeMe()

        except Exception as e:
            log_error("on_pushCancle_pressed", e, "canceling entity edit")
            makeMessageBox(f"Error canceling: {str(e)}")

    def on_list_pending_variables_double_clicked(self, index):
        """Handle double-click on pending variables list - go directly to equation selection"""
        
        # Stop the single-click timer to prevent classification dialog from showing
        self.click_timer.stop()
        self.pending_click_data = None
        
        # Get the model and item from the index
        model = self.ui.list_not_defined_variables.model()
        if model and index.isValid():
            item = model.itemFromIndex(index)
            if item:
                # Get the text and data from the clicked item
                item_text = item.text()
                item_data = item.data(QtCore.Qt.UserRole)
                
                # Extract variable ID from the item text
                # Format is typically: "label (ID: var_id, Network: network)"
                var_id = item_data.get('id')
                var_label = item_data.get('label')
                var_network = item_data.get('network')
                
                # Go directly to equation association editor for this variable
                message = {
                        "event"      : "def_variable",
                        "var_id"     : var_id,
                        "var_label"  : var_label,
                        "var_network": var_network
                        }
                self.message.emit(message)

    def on_list_pending_variables_single_clicked(self, index):
        """Handle single click on pending variables list - store for potential double-click"""
        
        # Get the sender widget to determine which list was clicked
        sender = self.sender()
        if not sender:
            return
            
        # Get the model and item from the index
        model = sender.model()
        if model and index.isValid():
            item = model.itemFromIndex(index)
            if item:
                # Get the text and data from the clicked item
                item_text = item.text()
                item_data = item.data(QtCore.Qt.UserRole)
                
                # Extract variable information
                var_id = item_data.get('id')
                var_label = item_data.get('label')
                var_network = item_data.get('network')
                
                # Determine which list was clicked
                list_name = sender.objectName() if hasattr(sender, 'objectName') else 'unknown'
                
                # Store click data for potential double-click handling
                self.pending_click_data = {
                    'type': 'classification',
                    'index': index,
                    'var_id': var_id,
                    'var_label': var_label,
                    'var_network': var_network,
                    'sender': sender,
                    'list_name': list_name
                    }
                
                # Start timer to wait for potential double-click
                self.click_timer.start(250)  # 250ms delay for double-click detection
        else:
            # Clear pending click data if invalid click
            self.pending_click_data = None

    def handle_single_click(self):
        """Handle single click after timer expires (if no double-click occurred)"""
        if self.pending_click_data:
            click_data = self.pending_click_data
            self.pending_click_data = None
            
            # Extract variable information from stored click data
            var_id = click_data.get('var_id')
            var_label = click_data.get('var_label')
            var_network = click_data.get('var_network')
            list_name = click_data.get('list_name', 'unknown')
            
            # Check if we're in reservoir editing mode
            is_reservoir_mode = "constant|infinity" in self.current_entity_data["entity_type"]#'reservoir' in self.mode.lower()
            
            # Handle different behavior based on which list was clicked
            if var_id:
                if list_name in ['list_inputs', 'list_outputs', 'list_instantiate', 'list_not_defined_variables']:
                    # Show classification dialog for these lists
                    from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QRadioButton, QPushButton, QDialogButtonBox
                    from PyQt5.QtCore import Qt
                    from OntologyBuilder.BehaviourLinker_v01.UIs.class_selector import Ui_Dialog
                    
                    # Create dialog
                    dialog = QDialog()
                    if is_reservoir_mode:
                        dialog.setWindowTitle("Variable Classification (Reservoir Mode)")
                    else:
                        dialog.setWindowTitle("Variable Classification")
                    dialog.resize(200, 150)
                    
                    # Setup UI
                    ui = Ui_Dialog()
                    ui.setupUi(dialog)
                    
                    # Set default selection based on current entity state
                    if hasattr(self, 'current_entity') and self.current_entity:
                        # Check manual classifications first
                        manual_classifications = getattr(self.current_entity, 'local_variable_classifications', {})
                        current_classifications = manual_classifications.get(var_id, {}).get('classification', ['none'])
                        
                        # Handle both single string and list of classifications
                        if isinstance(current_classifications, list):
                            # Multiple classifications - check first one for default
                            current_classification = current_classifications[0] if current_classifications else 'none'
                        else:
                            # Legacy single classification
                            current_classification = current_classifications
                        
                        if current_classification == "input":
                            ui.select_input.setChecked(True)
                        elif current_classification == "output":
                            ui.select_output.setChecked(True)
                        elif current_classification == "instantiate":
                            ui.radioButton.setChecked(True)
                        else:
                            ui.select_none.setChecked(True)
                        
                        # If multiple classifications, check all applicable boxes
                        if isinstance(current_classifications, list):
                            for classification in current_classifications:
                                if classification == "input":
                                    ui.select_input.setChecked(True)
                                elif classification == "output":
                                    ui.select_output.setChecked(True)
                                elif classification == "instantiate":
                                    ui.radioButton.setChecked(True)
                    
                    # Make radio buttons non-exclusive to allow multiple selections
                    
                    # Alternative: Convert to checkboxes for reliable multiple selection
                    ui.select_input.setCheckable(True)
                    ui.select_output.setCheckable(True) 
                    ui.radioButton.setCheckable(True)
                    ui.select_none.setCheckable(True)
                    
                    # Add instruction label for reservoir mode
                    if is_reservoir_mode:
                        ui.buttonGroup.setExclusive(False)
                        instruction_label = QLabel("Reservoir mode: Multiple selections allowed")
                        instruction_label.setStyleSheet("QLabel { color: blue; font-style: italic; }")
                        ui.verticalLayout.insertWidget(1, instruction_label)  # Insert after main label
                    
                    # Add OK button to close dialog (since auto-close is disabled)
                    ok_button = QPushButton("OK")
                    ok_button.clicked.connect(dialog.accept)
                    ui.verticalLayout.addWidget(ok_button)
                    
                    # Debug: Print initial state
                    print(f"DEBUG: Reservoir mode: {is_reservoir_mode}")
                    print(f"DEBUG: Button group exclusive property: {ui.buttonGroup.exclusive}")
                    print(f"DEBUG: Button group set to non-exclusive: {not ui.buttonGroup.exclusive}")
                    
                    # Connect radio buttons to close dialog when selected
                    def on_radio_selected():
                        # dialog.accept()
                        pass
                    
                    ui.select_input.toggled.connect(on_radio_selected)
                    ui.select_output.toggled.connect(on_radio_selected)
                    ui.radioButton.toggled.connect(on_radio_selected)  # instantiate radio button
                    ui.select_none.toggled.connect(on_radio_selected)
                    
                    # Show dialog and get result
                    if dialog.exec_() == QDialog.Accepted:
                        # Debug: Print all button states
                        print(f"DEBUG: mode: {self.mode} is reservoir mode {is_reservoir_mode}")
                        print(f"DEBUG: Input checked: {ui.select_input.isChecked()}")
                        print(f"DEBUG: Output checked: {ui.select_output.isChecked()}")
                        print(f"DEBUG: Instantiate checked: {ui.radioButton.isChecked()}")
                        print(f"DEBUG: None checked: {ui.select_none.isChecked()}")
                        
                        # Collect all checked classifications (since buttons are now non-exclusive)
                        classifications = []
                        if ui.select_input.isChecked():
                            classifications.append("input")
                        if ui.select_output.isChecked():
                            classifications.append("output")
                        if ui.radioButton.isChecked():  # instantiate radio button
                            classifications.append("instantiate")
                        
                        print(f"DEBUG: Collected classifications: {classifications}")
                        
                        # Handle multiple classifications
                        if not classifications:
                            print("DEBUG: No classifications selected")
                            return
                            
                        print(f"DEBUG: Selected classifications: {classifications}")
                        
                        # Reservoir mode specific handling
                        # if is_reservoir_mode:
                        #     print(f"DEBUG: Reservoir mode - allowing multiple classifications")
                        #     # In reservoir mode, we might want to handle multiple classifications differently
                        #     # For now, we'll still use primary classification but log all of them
                        #     if len(classifications) > 1:
                        #         print(f"DEBUG: Multiple classifications in reservoir mode: {classifications}")
                        #         # TODO: Implement reservoir-specific multiple classification logic
                        #         # - Could create multiple variable instances
                        #         # - Could apply all classifications to same variable
                        #         # - Could ask user to resolve conflicts
                        #
                        # # For multiple classifications, we need to decide how to handle them
                        # # Option 1: Use the first one (current behavior)
                        # # Option 2: Apply all classifications (if supported)
                        # # Option 3: Ask user to choose primary classification
                        #
                        # # For now, let's use the first one but log all of them
                        # primary_classification = classifications[0]
                        # print(f"DEBUG: Using primary classification: {primary_classification}")
                        # print(f"DEBUG: All selected classifications would be: {classifications}")
                        #
                        # # TODO: Implement proper multiple classification handling
                        # # For now, you could:
                        # # 1. Create multiple variable entries
                        # # 2. Ask user to choose primary classification
                        # # 3. Apply business rules for multiple classifications
                        #
                        # Handle multiple classifications using the new list-based system
                        if not classifications:
                            print("DEBUG: No classifications selected")
                            return
                            
                        print(f"DEBUG: Selected classifications: {classifications}")
                        
                        # Use the new list-based classification system
                        # This allows a variable to belong to multiple lists simultaneously
                        if hasattr(self, 'current_entity') and self.current_entity:
                            # Update the classification using the new system
                            self.current_entity.change_classification(var_id, classifications)
                            print(f"DEBUG: Updated classification for {var_id} to {classifications}")
                            
                            # Refresh UI to show the change
                            self.populate_lists_from_entity(self.current_entity)
                            print(f"DEBUG: Refreshed UI lists")

                            
                            # Show success message
                            # from OntologyBuilder.BehaviourLinker_v01.resources.pop_up_message_box import makeMessageBox
                            # makeMessageBox(f"Variable {var_label} moved to {classification} list", "Success")

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

            # Launch the BehaviorAssociation editor in state variable selection mode
            assignments = launch_behavior_association_editor(self.ontology_container, entity_type_info, 'state', self.current_entity)

            if assignments:
                # Process the state variable selection
                self.handle_state_variable_selection(assignments)
            else:
                # No state variable selected
                pass

        except Exception as e:
            log_error("launch_state_variable_selector", e, "launching state variable selector")
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

            # Launch the BehaviorAssociation editor in new variable addition mode
            assignments = launch_behavior_association_editor(self.ontology_container, entity_type_info, 'all', self.current_entity)

            if assignments:
                # Process the new variable addition
                self.handle_new_variable_addition(assignments)
            else:
                pass

        except Exception as e:
            log_error("launch_new_variable_selector", e, "launching new variable selector")
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
            # State variable selected

            # Extract the selected variable
            root_variable = assignments.get('root_variable')
            if root_variable:
                # Move to edit mode after state selection (start with no selection)
                self.set_mode("edit_no_selection")
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
                            'entity_id'    : getattr(self.current_entity, 'entity_id', ''),
                            'var_eq_forest': getattr(self.current_entity, 'var_eq_forest', []),
                            'output_vars'  : getattr(self.current_entity, 'output_vars', []),
                            'input_vars'   : getattr(self.current_entity, 'input_vars', []),
                            'init_vars'    : getattr(self.current_entity, 'init_vars', []),
                            'integrators'  : getattr(self.current_entity, 'integrators', {})
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
            log_error("handle_state_variable_selection", e, "handling state variable selection")
            makeMessageBox(f"Error handling state variable selection: {str(e)}")

    def handle_new_variable_addition(self, assignments):
        """Handle new variable addition in edit mode"""
        try:
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
                            'entity_id'    : getattr(self.current_entity, 'entity_id', ''),
                            'var_eq_forest': getattr(self.current_entity, 'var_eq_forest', []),
                            'output_vars'  : getattr(self.current_entity, 'output_vars', []),
                            'input_vars'   : getattr(self.current_entity, 'input_vars', []),
                            'init_vars'    : getattr(self.current_entity, 'init_vars', []),
                            'integrators'  : getattr(self.current_entity, 'integrators', {})
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
            log_error("handle_new_variable_addition", e, "handling new variable addition")
            makeMessageBox(f"Error handling new variable addition: {str(e)}")

    def update_entity_from_backend_entity(self, entity):
        """Update display when backend sends Entity object - Entity-only approach"""
        try:
            # Store current entity
            self.current_entity = entity

            # Set mode to edit when working with existing entity
            if self.mode not in ["edit_no_selection", "edit_with_selection", "edit_no_selection_node", "edit_with_selection_node", 
                                 "edit_no_selection_arc", "edit_with_selection_arc", "edit_reservoir", "edit_with_selection_reservoir"]:
                # Check if this is a reservoir entity
                if hasattr(self, 'current_entity_data') and self.current_entity_data:
                    entity_type = self.current_entity_data.get('entity_type', '')
                    if 'constant|infinity' in entity_type:
                        self.set_mode("edit_reservoir")  # Use reservoir-specific edit mode
                    else:
                        self.set_mode("edit_no_selection")  # Start with no selection
                else:
                    self.set_mode("edit_no_selection")  # Default to regular edit mode

            # Use Entity methods directly for all lists
            self.populate_lists_from_entity(entity)

            # Update Accept button visibility based on entity content
            self.update_accept_button_visibility()

        except Exception as e:
            log_error("update_entity_from_backend_entity", e, f"updating display for {getattr(entity, 'entity_id', 'unknown entity')}")
            makeMessageBox(f"Error updating entity display: {str(e)}")

    def update_entity_from_backend_new(self, entity_data):
        """Deprecated - redirect to Entity-only approach"""
        # Extract Entity object from entity_data
        if 'entity_object' in entity_data and entity_data['entity_object']:
            self.update_entity_from_backend_entity(entity_data['entity_object'])
        else:
            pass
        """Update entity display when backend sends updated entity data"""
        try:
            # Check if we have an entity object in the data
            if 'entity_object' in entity_data:
                entity = entity_data['entity_object']
                self.current_entity = entity
                # Use the complete entity population method
                self.populate_lists_from_entity(entity)
            else:
                # Fallback to current_entity_data if no entity object
                self.populate_from_entity_data_fallback(entity_data)

        except Exception as e:
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
            pass

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
