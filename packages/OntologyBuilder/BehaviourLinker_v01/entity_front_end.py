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

        # Add left-click context menus for all lists


        if hasattr(self.ui, 'list_equations'):

            self.ui.list_equations.clicked.connect(self.on_left_click_context_menu)
        else:
            # Don't connect list_not_defined_variables here - it's already connected above
            self.ui.list_inputs.clicked.connect(self.on_left_click_context_menu)
            self.ui.list_outputs.clicked.connect(self.on_left_click_context_menu)
            print(f"=== CONNECTION DEBUG: Connected left-click handlers for inputs/outputs ===")
        self.ui.list_instantiate.clicked.connect(self.on_left_click_context_menu)
        self.ui.list_integrators.clicked.connect(self.on_left_click_context_menu)
        self.ui.list_included_variables.clicked.connect(self.on_left_click_context_menu)

        # Setup right-click context menus for all variable lists
        self._setup_right_click_context_menus()

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
        self.click_timer.timeout.connect(self.on_single_click_timeout)
        self.pending_click_data = None
        changed = False

    def _setup_right_click_context_menus(self):
        """Setup right-click context menus for all variable lists"""
        try:
            from PyQt5 import QtWidgets
            from PyQt5.QtCore import Qt

            # All lists that should have right-click context menus
            lists_with_context_menu = [
                    self.ui.list_outputs,
                    self.ui.list_inputs,
                    self.ui.list_instantiate,
                    self.ui.list_integrators,
                    self.ui.list_included_variables,
                    self.ui.list_not_defined_variables
                    # Remove equations list to avoid signal conflicts with left-click
                    # self.ui.list_equations
                    ]

            for list_widget in lists_with_context_menu:
                try:
                    # Enable custom context menu
                    list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
                    # Connect context menu request signal
                    list_widget.customContextMenuRequested.connect(
                            lambda pos, widget=list_widget: self.on_context_menu_requested(pos, widget)
                            )

                except Exception as e:
                    list_name = list_widget.objectName() if hasattr(list_widget, 'objectName') else 'unknown'
                    log_error("_setup_right_click_context_menus", e, f"setting up {list_name} context menu")

        except Exception as e:
            log_error("_setup_right_click_context_menus", e, "main right-click context menu setup")

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

    def _setup_context_menus(self):
        """Setup right-click context menus for all variable lists"""
        try:
            from PyQt5 import QtWidgets
            from PyQt5.QtCore import Qt

            # All lists that should have context menus
            lists_with_context_menu = [
                    self.ui.list_outputs,
                    self.ui.list_inputs,
                    self.ui.list_instantiate,
                    self.ui.list_integrators,
                    self.ui.list_included_variables,
                    self.ui.list_not_defined_variables
                    ]

            for list_widget in lists_with_context_menu:
                try:
                    # Enable custom context menu
                    list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
                    # Connect the context menu request signal
                    list_widget.customContextMenuRequested.connect(
                            lambda pos, widget=list_widget: self.on_context_menu_requested(pos, widget)
                            )
                except Exception as e:
                    log_error("_setup_context_menus", e, f"setting up {list_widget.objectName()}")

        except Exception as e:
            log_error("_setup_context_menus", e, "main context menu setup")

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
        """Update Accept button visibility based on current automaton mode"""
        # Use automaton to determine visibility
        if hasattr(self, 'mode') and self.mode:
            # Get current mode's button configuration
            button_config = gui_automaton.get(self.mode, {})
            if button_config:
                should_show = button_config.get("accept", False)
                if should_show:
                    self.gui_objects["buttons"]["accept"].show()
                else:
                    self.gui_objects["buttons"]["accept"].hide()
            else:
                # Default: hide accept button if mode not found
                self.gui_objects["buttons"]["accept"].hide()
        else:
            # No mode set: hide accept button
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
                    # Create proper data structure for equations
                    eq_id = str(eq_info)
                    eq_data = {
                            'id'     : eq_id,
                            'label'  : eq_id,
                            'network': 'unknown'  # Equations don't have network info
                            }
                    self.add_to_list(self.ui.list_equations, eq_id, getIcon("equation"), data=eq_data)

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
            
            # IMPORTANT: Re-connect left-click handlers after refresh to ensure they work
            self.ui.list_outputs.clicked.connect(self.on_left_click_context_menu)
            self.ui.list_inputs.clicked.connect(self.on_left_click_context_menu)
            self.ui.list_instantiate.clicked.connect(self.on_left_click_context_menu)
            self.ui.list_integrators.clicked.connect(self.on_left_click_context_menu)
            print(f"=== CONNECTION DEBUG: Re-connected left-click handlers after refresh ===")
            self.refresh_list_widget_settings(self.ui.list_included_variables, 'entity_variables')

            variables = self.ontology_container.variables

            # Build local variable classifications if this is the first time
            if is_first_time:
                entity.build_local_variable_classifications(variables)

            # Populate output variables list
            output_vars = entity.get_output_vars(self.ontology_container)
            print(f"=== POPULATE DEBUG: Output vars: {output_vars} ===")
            for var_id in output_vars:
                if var_id in variables:
                    var_data = variables[var_id]
                    var_info = {
                            'id'     : var_id,
                            'label'  : var_data.get('label', var_id),
                            'network': var_data.get('network', 'unknown')
                            }
                    self.add_variable_to_list(self.ui.list_outputs, var_info)
                    print(f"=== POPULATE DEBUG: Added output {var_id} ===")

            # Populate input variables list
            input_vars = entity.get_input_vars()
            print(f"=== POPULATE DEBUG: Input vars: {input_vars} ===")
            for var_id in input_vars:
                if var_id in variables:
                    var_data = variables[var_id]
                    var_info = {
                            'id'     : var_id,
                            'label'  : var_data.get('label', var_id),
                            'network': var_data.get('network', 'unknown')
                            }
                    self.add_variable_to_list(self.ui.list_inputs, var_info)
                    print(f"=== POPULATE DEBUG: Added input {var_id} ===")

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

                else:
                    pass

            


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

                else:
                    pass

            


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
                # Safely get LHS variable with error handling to prevent SIGSEGV
                try:
                    if hasattr(entity, 'getLHS') and entity.getLHS:
                        var_id = entity.getLHS(eq_id)
                        if var_id is None:

                            var_id = eq_id  # Fallback to equation ID
                        else:
                            pass

                    else:
                        pass

                        var_id = eq_id  # Fallback to equation ID
                except Exception as e:

                    var_id = eq_id  # Fallback to equation ID

                    
                icon = self.ontology_container.equation_icons[eq_id]
                # Create proper data structure for equations
                eq_data = {
                        'id'     : var_id,
                        'eq_id'  : eq_id,
                        'label'  : eq_text,
                        'network': 'unknown'  # Equations don't have network info
                        }
                self.add_to_list(self.ui.list_equations, eq_text, icon, context='entity_equations', data=eq_data)

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
            print(f"=== FRONTEND DEBUG: pending_vars = {pending_vars} ===")

            for var_id in pending_vars:
                if var_id in variables:
                    var_data = variables[var_id]
                    var_info = {
                            'id'     : var_id,
                            'label'  : var_data.get('label', var_id),
                            'network': var_data.get('network', 'unknown')
                            }
                    print(f"=== FRONTEND DEBUG: Adding pending var {var_id} to list ===")
                    self.add_variable_to_list(self.ui.list_not_defined_variables, var_info)

            # Setup selection handlers now that lists are populated
            self._setup_selection_handlers()
            
            # DEBUG: Check list counts
            print(f"=== POPULATE DEBUG: List counts - Inputs: {self.ui.list_inputs.model().rowCount()}, Outputs: {self.ui.list_outputs.model().rowCount()}, Integrators: {self.ui.list_integrators.model().rowCount()} ===")

            # Update mode based on selection after populating lists
            self._update_mode_based_on_selection()

        except Exception as e:
            import traceback
            error_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'stack_trace': traceback.format_exc(),
                'entity_id': getattr(entity, 'entity_id', 'unknown entity') if entity else 'no entity',
                'entity_type': type(entity).__name__ if entity else 'no entity'
            }
            

            print(f"  Error Type: {error_details['error_type']}")
            print(f"  Error Message: {error_details['error_message']}")
            print(f"  Entity ID: {error_details['entity_id']}")
            print(f"  Entity Type: {error_details['entity_type']}")
            print(f"  Stack Trace:\n{error_details['stack_trace']}")
            
            log_error("populate_lists_from_entity", e,
                      f"populating lists for {error_details['entity_id']} - {error_details['error_type']}: {error_details['error_message']}")
            makeMessageBox(f"Error updating entity lists: {error_details['error_type']}: {error_details['error_message']}\n\nCheck console for detailed stack trace.")

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
            
            # Check if variable has dependencies and warn user
            warning_msg = f"Delete variable {selected_var_id} from entity?"
            try:
                # Try to get dependencies to warn user
                if hasattr(self, 'current_entity') and self.current_entity:
                    entity = self.current_entity
                    if hasattr(entity, 'get_eq_for_var'):
                        deps = entity.get_eq_for_var(selected_var_id)
                        if deps:
                            warning_msg += f"\n\nWarning: This variable is used by equations: {', '.join(deps)}. Deleting it will also remove these equations and may affect other variables that depend on them."
            except Exception as e:
                pass

            
            result = makeMessageBox(warning_msg, buttons=["YES", "NO"])

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

    def on_single_click_timeout(self):
        """Handle single click timeout - show context menu"""
        if self.pending_click_data:
            index, sender = self.pending_click_data
            self.pending_click_data = None
            
            # Show the context menu for single click using the sender widget
            self.on_left_click_context_menu_for_widget(sender, index)

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

                # Go directly to equation dialog for this variable (equation editor is disabled)
                self.open_equation_dialog(var_id, var_label, var_network)

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
                self.pending_click_data = (index, sender)
                
                # Start timer to detect single vs double click
                self.click_timer.start(250)  # 250ms timeout
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
            is_reservoir_mode = "constant|infinity" in self.current_entity_data[
                "entity_type"]  # 'reservoir' in self.mode.lower()

            # Handle different behavior based on which list was clicked
            if var_id:
                if list_name in ['list_inputs', 'list_outputs', 'list_instantiate', 'list_not_defined_variables']:
                    # Show classification dialog for these lists
                    from PyQt5.QtWidgets import QDialog, QLabel, QPushButton
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






                        # Collect all checked classifications (since buttons are now non-exclusive)
                        classifications = []
                        if ui.select_input.isChecked():
                            classifications.append("input")
                        if ui.select_output.isChecked():
                            classifications.append("output")
                        if ui.radioButton.isChecked():  # instantiate radio button
                            classifications.append("instantiate")



                        # Handle multiple classifications
                        if not classifications:

                            return



                        # Reservoir mode specific handling
                        # if is_reservoir_mode:

                        #     # In reservoir mode, we might want to handle multiple classifications differently
                        #     # For now, we'll still use primary classification but log all of them
                        #     if len(classifications) > 1:

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


                        #
                        # # TODO: Implement proper multiple classification handling
                        # # For now, you could:
                        # # 1. Create multiple variable entries
                        # # 2. Ask user to choose primary classification
                        # # 3. Apply business rules for multiple classifications
                        #
                        # Handle multiple classifications using the new list-based system
                        if not classifications:

                            return



                        # Use the new list-based classification system
                        # This allows a variable to belong to multiple lists simultaneously
                        if hasattr(self, 'current_entity') and self.current_entity:
                            # Update the classification using the new system
                            self.current_entity.change_classification(var_id, classifications)


                            # Refresh UI to show the change
                            self.populate_lists_from_entity(self.current_entity)


                            # Show success message
                            # from OntologyBuilder.BehaviourLinker_v01.resources.pop_up_message_box import makeMessageBox
                            # makeMessageBox(f"Variable {var_label} moved to {classification} list", "Success")

    def open_context_menu_directly(self, sender, index, var_id, var_label, var_network, list_name):
        """Open context menu directly (bypasses selection system)"""
        try:
            from PyQt5.QtWidgets import QMenu, QAction
            from PyQt5.QtCore import Qt

            # Create context menu
            context_menu = QMenu(sender)

            # Add actions based on which list was clicked
            if list_name == 'list_equations':
                # Equations: No menu - equations list is read-only

                return  # Don't create any menu for equations list
                
            elif list_name == 'list_not_defined_variables':
                # Pending variables: equation dialog option (re-enabled with simple dialog)
                equation_action = QAction("Equation Dialog", sender)
                equation_action.triggered.connect(lambda: self.open_equation_dialog(var_id, var_label, var_network))
                context_menu.addAction(equation_action)

            # Show context menu at the item position
            visual_rect = sender.visualRect(index)
            if visual_rect.isValid():
                item_pos = visual_rect.topLeft()
                global_pos = sender.mapToGlobal(item_pos)

                context_menu.exec_(global_pos)

        except Exception as e:
            log_error("open_context_menu_directly", e, f"opening direct context menu for {var_id}")

    def on_left_click_context_menu(self, index):
        """Handle left-click context menu on variable lists"""
        try:
            from PyQt5.QtWidgets import QMenu, QAction
            from PyQt5.QtCore import Qt

            # Get the sender widget to determine which list was clicked
            sender = self.sender()
            if not sender:
                return

            list_name = sender.objectName() if hasattr(sender, 'objectName') else 'unknown'
            print(f"=== LEFT-CLICK DEBUG: Clicked on {list_name} ===")

            # Get the index and model
            model = sender.model()
            if not model or not index.isValid():
                print(f"=== LEFT-CLICK DEBUG: No model or invalid index ===")
                return

            # Get variable information from model index data
            item_data = model.data(index, QtCore.Qt.UserRole)
            if not item_data:
                print(f"=== LEFT-CLICK DEBUG: No item data ===")
                return

            var_id = item_data.get('id')
            var_label = item_data.get('label', var_id)
            var_network = item_data.get('network')

            if not var_id:
                print(f"=== LEFT-CLICK DEBUG: No var_id ===")
                return

            print(f"=== LEFT-CLICK DEBUG: Creating menu for {var_id} in {list_name} ===")

            # Create context menu
            context_menu = QMenu(sender)

            # Add actions based on which list was clicked
            if list_name == 'list_not_defined_variables':
                # Pending variables: classification + equation dialog
                classification_action = QAction("Classification", sender)
                classification_action.triggered.connect(lambda: self.open_classification_dialog(var_id, var_label, list_name))
                context_menu.addAction(classification_action)

                equation_action = QAction("Equation Dialog", sender)
                equation_action.triggered.connect(lambda: self.open_equation_dialog(var_id, var_label, var_network))
                context_menu.addAction(equation_action)

            elif list_name == 'list_inputs':
                # Inputs: classification only
                classification_action = QAction("Classification", sender)
                classification_action.triggered.connect(lambda: self.open_classification_dialog(var_id, var_label, list_name))
                context_menu.addAction(classification_action)

            elif list_name == 'list_outputs':
                # Outputs: classification only
                classification_action = QAction("Classification", sender)
                classification_action.triggered.connect(lambda: self.open_classification_dialog(var_id, var_label, list_name))
                context_menu.addAction(classification_action)

            elif list_name == 'list_instantiate':
                # Instantiate: classification only
                classification_action = QAction("Classification", sender)
                classification_action.triggered.connect(lambda: self.open_classification_dialog(var_id, var_label, list_name))
                context_menu.addAction(classification_action)

            elif list_name == 'list_integrators':
                # Integrators: no context menu (read-only)
                return  # Don't create any menu for integrators list

            elif list_name == 'list_included_variables':
                # Included: delete option
                delete_action = QAction("Delete", sender)
                delete_action.triggered.connect(lambda: self.delete_variable_from_context(var_id, var_label))
                context_menu.addAction(delete_action)

            if list_name == 'list_equations':
                # Equations: No menu - equations list is read-only

                return  # Don't create any menu for equations list

            # Show context menu at clicked item position (more reliable than cursor)
            # Get the visual rectangle of the clicked item
            visual_rect = sender.visualRect(index)
            if visual_rect.isValid():
                # Position menu at the bottom-left of the item
                item_pos = visual_rect.topLeft()
                global_pos = sender.mapToGlobal(item_pos)

                context_menu.exec_(global_pos)

            else:
                # Fallback to cursor position
                cursor_pos = sender.cursor().pos()
                global_pos = sender.mapToGlobal(cursor_pos)
                context_menu.exec_(global_pos)

        except Exception as e:
            log_error("on_left_click_context_menu", e, "handling left-click context menu")

    def on_left_click_context_menu_for_widget(self, sender, index):
        """Handle left-click context menu for a specific widget and index"""
        try:
            from PyQt5.QtWidgets import QMenu, QAction
            from PyQt5.QtCore import Qt

            if not sender:
                return

            # Get the index and model
            model = sender.model()
            if not model or not index.isValid():
                return

            # Get variable information from model index data
            item_data = model.data(index, QtCore.Qt.UserRole)
            if not item_data:
                return

            var_id = item_data.get('id')
            var_label = item_data.get('label', var_id)
            var_network = item_data.get('network')
            list_name = sender.objectName() if hasattr(sender, 'objectName') else 'unknown'

            if not var_id:
                return

            # Create context menu
            context_menu = QMenu(sender)

            # Add actions based on which list was clicked
            if list_name == 'list_not_defined_variables':
                # Pending variables: classification + equation dialog
                classification_action = QAction("Classification", sender)
                classification_action.triggered.connect(lambda: self.open_classification_dialog(var_id, var_label, list_name))
                context_menu.addAction(classification_action)

                equation_action = QAction("Equation Dialog", sender)
                equation_action.triggered.connect(lambda: self.open_equation_dialog(var_id, var_label, var_network))
                context_menu.addAction(equation_action)

            elif list_name == 'list_inputs':
                # Inputs: classification only
                classification_action = QAction("Classification", sender)
                classification_action.triggered.connect(lambda: self.open_classification_dialog(var_id, var_label, list_name))
                context_menu.addAction(classification_action)

            elif list_name == 'list_outputs':
                # Outputs: classification only
                classification_action = QAction("Classification", sender)
                classification_action.triggered.connect(lambda: self.open_classification_dialog(var_id, var_label, list_name))
                context_menu.addAction(classification_action)

            elif list_name == 'list_instantiate':
                # Instantiate: classification only
                classification_action = QAction("Classification", sender)
                classification_action.triggered.connect(lambda: self.open_classification_dialog(var_id, var_label, list_name))
                context_menu.addAction(classification_action)

            elif list_name == 'list_integrators':
                # Integrators: no context menu (read-only)
                return  # Don't create any menu for integrators list

            elif list_name == 'list_included_variables':
                # Included variables: equation dialog only
                equation_action = QAction("Equation Dialog", sender)
                equation_action.triggered.connect(lambda: self.open_equation_dialog(var_id, var_label, var_network))
                context_menu.addAction(equation_action)

            # Show context menu at the item position
            visual_rect = sender.visualRect(index)
            if visual_rect.isValid():
                item_pos = visual_rect.topLeft()
                global_pos = sender.mapToGlobal(item_pos)
                context_menu.exec_(global_pos)

        except Exception as e:
            log_error("on_left_click_context_menu_for_widget", e, "handling left-click context menu for widget")

    def on_context_menu_requested(self, pos, list_widget):
        """Handle right-click context menu on variable lists"""
        try:
            from PyQt5.QtWidgets import QMenu, QAction
            from PyQt5.QtCore import Qt

            # Get the index at the clicked position (QListView method)
            index = list_widget.indexAt(pos)
            if not index.isValid():
                return  # No item clicked

            model = list_widget.model()
            if not model:
                return

            # Get variable information from model index data
            item_data = model.data(index, QtCore.Qt.UserRole)
            if not item_data:
                return

            var_id = item_data.get('id')
            var_label = item_data.get('label', var_id)
            var_network = item_data.get('network')
            list_name = list_widget.objectName() if hasattr(list_widget, 'objectName') else 'unknown'

            if not var_id:
                return

            # Create context menu
            context_menu = QMenu(list_widget)

            # Add actions based on which list was clicked
            if list_name == 'list_not_defined_variables':
                # For pending variables, offer equation selection as primary
                equation_action = QAction("Open Equation Dialog", list_widget)
                equation_action.triggered.connect(lambda: self.open_equation_dialog(var_id, var_label, var_network))
                context_menu.addAction(equation_action)

                # Add separator and classification option
                context_menu.addSeparator()
                classification_action = QAction("Change Classification", list_widget)
                classification_action.triggered.connect(lambda: self.open_classification_dialog(var_id, var_label, list_name))
                context_menu.addAction(classification_action)
            else:
                # For other lists, classification is now the primary right-click action
                classification_action = QAction("Change Classification", list_widget)
                classification_action.triggered.connect(lambda: self.open_classification_dialog(var_id, var_label, list_name))
                context_menu.addAction(classification_action)

                # Add separator and delete option
                context_menu.addSeparator()
                if list_name not in ['list_not_defined_variables']:  # Don't delete from pending list
                    delete_action = QAction("Delete Variable", list_widget)
                    delete_action.triggered.connect(lambda: self.delete_variable_from_context(var_id, var_label))
                    context_menu.addAction(delete_action)

            # Show context menu at cursor position
            global_pos = list_widget.mapToGlobal(pos)
            context_menu.exec_(global_pos)

        except Exception as e:
            log_error("on_context_menu_requested", e, "handling context menu")

    def open_equation_dialog(self, var_id, var_label, var_network):
        """Open the original equation selection dialog for a variable"""
        try:
            # Get variable data from ontology container
            if hasattr(self, 'ontology_container') and self.ontology_container:
                if var_id in self.ontology_container.variables:
                    # Send message to backend to launch equation selector
                    message = {
                        "event": "def_variable",
                        "var_id": var_id,
                        "var_label": var_label,
                        "var_network": var_network
                    }
                    self.message.emit(message)
                else:
                    # Variable not found
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Variable Not Found", 
                                      f"Variable {var_id} not found in ontology container")
            else:
                # No ontology container
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "No Ontology", 
                                  "No ontology container available for equation selection")
                
        except Exception as e:
            # Fallback to simple dialog if original dialog fails
            print(f"Original equation dialog failed, falling back to simple dialog: {e}")
            self._open_simple_equation_dialog(var_id, var_label, var_network)

    def _open_simple_equation_dialog(self, var_id, var_label, var_network):
        """Fallback simple equation selection dialog"""
        try:

            
            # Create simple equation selection dialog
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout
            from PyQt5.QtCore import Qt
            
            dialog = QDialog()
            dialog.setWindowTitle(f"Select Equation for {var_label}")
            dialog.setModal(True)
            
            layout = QVBoxLayout()
            
            # Add title
            title = QLabel(f"Select equation for variable {var_label}:")
            layout.addWidget(title)
            
            # Add equation list
            equation_list = QListWidget()
            
            # Get available equations from ontology container
            if hasattr(self, 'ontology_container') and self.ontology_container:
                equations = getattr(self.ontology_container, 'equation_dictionary', {})

                
                # Add "No equation (initialization)" option
                no_eq_item = QListWidgetItem("No equation (initialization)")
                no_eq_item.setData(QtCore.Qt.UserRole, None)  # Store None for initialization
                equation_list.addItem(no_eq_item)
                
                # Add available equations
                for eq_id in sorted(equations.keys()):
                    item = QListWidgetItem(f"{eq_id}")
                    item.setData(QtCore.Qt.UserRole, eq_id)  # Store equation ID
                    equation_list.addItem(item)

            
            layout.addWidget(equation_list)
            
            # Add buttons
            button_layout = QHBoxLayout()
            ok_button = QPushButton("OK")
            cancel_button = QPushButton("Cancel")
            button_layout.addWidget(ok_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            
            # Handle button clicks
            def on_ok():
                selected_item = equation_list.currentItem()
                if selected_item:
                    equation_id = selected_item.data(QtCore.Qt.UserRole)

                    
                    # Create assignment result
                    assignments = {
                        'equation_id': equation_id,
                        'use_initialization': equation_id is None
                    }
                    
                    # Send message to backend
                    message = {
                        "event": "def_variable",
                        "var_id": var_id,
                        "var_label": var_label,
                        "var_network": var_network,
                        "assignments": assignments
                    }

                    self.message.emit(message)
                    
                dialog.accept()
            
            def on_cancel():

                dialog.reject()
            
            ok_button.clicked.connect(on_ok)
            cancel_button.clicked.connect(on_cancel)
            
            # Show dialog
            result = dialog.exec_()

            
        except Exception as e:
            log_error("open_equation_dialog", e, f"opening equation dialog for {var_id}")

    def launch_equation_editor(self, var_id, var_label, var_network):
        """Launch the proper equation association editor for a variable"""
        try:
            message = {
                "event": "def_variable",
                "var_id": var_id,
                "var_label": var_label,
                "var_network": var_network
            }
            self.message.emit(message)
        except Exception as e:
            log_error("launch_equation_editor", e, "launching equation editor")


    # Single-click method removed - right-click now handles classification
    def handle_classification_dialog(self, var_id, var_label, var_network, list_name):
        """Handle classification dialog directly (replaces handle_single_click logic)"""
        try:
            # Check if we're in reservoir editing mode
            is_reservoir_mode = "constant|infinity" in self.current_entity_data[
                "entity_type"]  # 'reservoir' in self.mode.lower()

            # Show classification dialog
            if var_id and list_name in ['list_inputs', 'list_outputs', 'list_instantiate', 'list_not_defined_variables']:
                from PyQt5.QtWidgets import QDialog, QLabel, QPushButton
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
                ui.select_input.setCheckable(True)
                ui.select_output.setCheckable(True)
                ui.radioButton.setCheckable(True)
                ui.select_none.setCheckable(True)

                # Add instruction label for reservoir mode
                if is_reservoir_mode:
                    ui.buttonGroup.setExclusive(False)
                    instruction_label = QLabel("Reservoir mode: Multiple selections allowed")
                    instruction_label.setStyleSheet("QLabel { color: blue; font-style: italic; }")
                    ui.verticalLayout.insertWidget(1, instruction_label)

                # Add OK button to close dialog
                ok_button = QPushButton("OK")
                ok_button.clicked.connect(dialog.accept)
                ui.verticalLayout.addWidget(ok_button)

                # Connect radio buttons to close dialog when selected
                def on_radio_selected():
                    pass

                ui.select_input.toggled.connect(on_radio_selected)
                ui.select_output.toggled.connect(on_radio_selected)
                ui.radioButton.toggled.connect(on_radio_selected)
                ui.select_none.toggled.connect(on_radio_selected)

                # Show dialog and get result
                if dialog.exec_() == QDialog.Accepted:
                    # Collect all checked classifications
                    classifications = []
                    if ui.select_input.isChecked():
                        classifications.append("input")
                    if ui.select_output.isChecked():
                        classifications.append("output")
                    if ui.radioButton.isChecked():
                        classifications.append("instantiate")

                    # Handle multiple classifications
                    if not classifications:
                        return

                    # Use the new list-based classification system
                    print(f"=== FRONTEND DEBUG: About to call change_classification ===")
                    print(f"=== FRONTEND DEBUG: hasattr(self, 'current_entity'): {hasattr(self, 'current_entity')} ===")
                    print(f"=== FRONTEND DEBUG: self.current_entity: {self.current_entity} ===")
                    print(f"=== FRONTEND DEBUG: var_id: {var_id}, classifications: {classifications} ===")
                    
                    if hasattr(self, 'current_entity') and self.current_entity:
                        # Update the classification using the new system
                        print(f"=== FRONTEND DEBUG: Calling change_classification ===")
                        self.current_entity.change_classification(var_id, classifications)
                        print(f"=== FRONTEND DEBUG: change_classification completed ===")
                        
                        # Refresh UI to show the change
                        self.populate_lists_from_entity(self.current_entity)
                    else:
                        print(f"=== FRONTEND DEBUG: SKIPPING change_classification - no current_entity ===")


        except Exception as e:
            log_error("handle_classification_dialog", e, f"handling classification dialog for {var_id}")

    def open_classification_dialog(self, var_id, var_label, list_name):
        """Open classification dialog for a variable (from context menu)"""
        try:
            # Call the direct handler instead of using the old click-based system
            self.handle_classification_dialog(var_id, var_label, None, list_name)
        except Exception as e:
            log_error("open_classification_dialog", e, f"opening classification dialog for {var_id}")

    def delete_variable_from_context(self, var_id, var_label):
        """Delete a variable from context menu"""
        try:
            # Select the variable in the appropriate list first
            selected_var_id = self.get_selected_variable_id()
            if selected_var_id == var_id:
                # If it's already selected, just trigger delete
                self.on_pushDeleteVariable_pressed()
            else:
                # Need to select it first - this is complex, so show a message
                from OntologyBuilder.BehaviourLinker_v01.resources.pop_up_message_box import makeMessageBox
                makeMessageBox(f"Please select '{var_label}' in the list and use the Delete button", "Delete Variable")

        except Exception as e:
            log_error("delete_variable_from_context", e, f"deleting variable {var_id}")

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
            assignments = launch_behavior_association_editor(self.ontology_container, entity_type_info, 'state',
                                                             self.current_entity)

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
            assignments = launch_behavior_association_editor(self.ontology_container, entity_type_info, 'all',
                                                             self.current_entity)

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
                    self.status_label.setText(
                            f"New variable '{assignments.get('variable_label', root_variable)}' added to entity")
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
            
            # Update current_entity_data to keep it in sync with the entity
            if hasattr(entity, 'to_dict'):
                self.current_entity_data = entity.to_dict()
            else:
                # Fallback: create basic entity data structure
                self.current_entity_data = {
                    'entity_object': entity,
                    'entity_type': getattr(entity, 'entity_type', ''),
                    'name': getattr(entity, 'name', ''),
                }

            # Set mode to edit when working with existing entity
            if self.mode not in ["edit_no_selection", "edit_with_selection", "edit_no_selection_node",
                                 "edit_with_selection_node",
                                 "edit_no_selection_arc", "edit_with_selection_arc", "edit_reservoir",
                                 "edit_with_selection_reservoir"]:
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
            log_error("update_entity_from_backend_entity", e,
                      f"updating display for {getattr(entity, 'entity_id', 'unknown entity')}")
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
            self.status_label.setText(
                    "No Entity object available - pending variable management must be done by Entity class")
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
