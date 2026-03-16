"""
Entity Editor UI Module
Handles all UI setup, management, and visual operations for the Entity Editor
"""

from PyQt5 import QtWidgets
from OntologyBuilder.BehaviourLinker_v01.UIs.entity_changes import Ui_entity_changes


class EntityEditorUI:
    """
    Manages all UI components and visual operations for the Entity Editor
    """
    
    def __init__(self, parent_dialog):
        """
        Initialize the UI manager
        
        Args:
            parent_dialog: The parent EntityEditorCore dialog
        """
        self.parent = parent_dialog
        self.ui = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the main UI components"""
        self.ui = Ui_entity_changes()
        self.ui.setupUi(self.parent)
        self._configure_ui_elements()
    
    def _configure_ui_elements(self):
        """Configure initial UI element properties"""
        # Configure list widgets
        self._configure_list_widgets()
        
        # Configure buttons
        self._configure_buttons()
        
        # Setup initial states
        self._setup_initial_states()
    
    def _configure_list_widgets(self):
        """Configure all list widgets with proper settings"""
        lists = [
            self.ui.list_inputs,
            self.ui.list_outputs,
            self.ui.list_instantiate,
            self.ui.list_not_defined_variables,
            self.ui.list_equations
        ]
        
        for list_widget in lists:
            # Set selection mode
            list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            
            # Set drag drop properties
            list_widget.setDragEnabled(True)
            list_widget.setAcceptDrops(True)
            list_widget.setDropIndicatorShown(True)
            
            # Set default font
            font = list_widget.font()
            font.setPointSize(10)
            list_widget.setFont(font)
    
    def _configure_buttons(self):
        """Configure all buttons with proper properties"""
        # Main action buttons
        self.ui.pushAccept.setEnabled(False)
        self.ui.pushCancle.setEnabled(True)
        
        # Variable addition buttons
        variable_buttons = [
            self.ui.pushAddVariable,
            self.ui.pushAddStateVariable,
            self.ui.pushAddTransport,
            self.ui.pushAddIntensitity,
            self.ui.pushDeleteVariable
        ]
        
        for button in variable_buttons:
            button.setEnabled(False)
    
    def _setup_initial_states(self):
        """Setup initial UI states"""
        # Hide advanced options by default
        self.ui.frame_advanced_options.hide()
        
        # Set default tab
        self.ui.tabWidget.setCurrentIndex(0)
        
        # Setup status indicators
        self._setup_status_indicators()
    
    def _setup_status_indicators(self):
        """Setup status indicators and labels"""
        # Entity type label
        self.ui.label_entity_type.setText("No entity selected")
        
        # Mode label
        self.ui.label_mode.setText("Normal mode")
        
        # Status bar (if exists)
        if hasattr(self.ui, 'statusBar'):
            self.ui.statusBar.showMessage("Ready")
    
    def populate_lists_from_entity(self, entity):
        """
        Populate all list widgets with data from the Entity object
        
        Args:
            entity: The entity object containing variable data
        """
        try:
            # Clear all lists first
            self.clear_all_lists()
            
            # Check if this is the first time lists are being calculated
            is_first_time = not hasattr(entity, 'classifications_initialized') or not entity.classifications_initialized
            
            # Get ontology container for variable data
            if hasattr(self.parent, 'ontology_container') and self.parent.ontology_container:
                variables = self.parent.ontology_container.variables
                
                # Build local variable classifications if this is the first time
                if is_first_time:
                    entity.build_local_variable_classifications(variables)
                
                # Populate each list
                self._populate_output_variables(entity, variables)
                self._populate_input_variables(entity, variables)
                self._populate_instantiate_variables(entity, variables)
                self._populate_pending_variables(entity, variables)
                self._populate_equation_variables(entity, variables)
                
                # Mark as initialized
                entity.classifications_initialized = True
            
        except Exception as e:
            print(f"Error populating lists from entity: {e}")
    
    def _populate_output_variables(self, entity, variables):
        """Populate the output variables list"""
        output_vars = entity.get_output_vars(self.parent.ontology_container)
        
        for var_id in output_vars:
            if var_id in variables:
                var_data = variables[var_id]
                label = var_data.get('label', var_id)
                self._add_item_to_list(self.ui.list_outputs, var_id, label)
    
    def _populate_input_variables(self, entity, variables):
        """Populate the input variables list"""
        input_vars = entity.get_input_vars(self.parent.ontology_container)
        
        for var_id in input_vars:
            if var_id in variables:
                var_data = variables[var_id]
                label = var_data.get('label', var_id)
                self._add_item_to_list(self.ui.list_inputs, var_id, label)
    
    def _populate_instantiate_variables(self, entity, variables):
        """Populate the instantiate variables list"""
        instantiate_vars = entity.get_instantiate_vars(self.parent.ontology_container)
        
        for var_id in instantiate_vars:
            if var_id in variables:
                var_data = variables[var_id]
                label = var_data.get('label', var_id)
                self._add_item_to_list(self.ui.list_instantiate, var_id, label)
    
    def _populate_pending_variables(self, entity, variables):
        """Populate the pending variables list"""
        pending_vars = entity.get_pending_vars(self.parent.ontology_container)
        
        for var_id in pending_vars:
            if var_id in variables:
                var_data = variables[var_id]
                label = var_data.get('label', var_id)
                self._add_item_to_list(self.ui.list_not_defined_variables, var_id, label)
    
    def _populate_equation_variables(self, entity, variables):
        """Populate the equation variables list"""
        equation_vars = entity.get_equation_vars(self.parent.ontology_container)
        
        for var_id in equation_vars:
            if var_id in variables:
                var_data = variables[var_id]
                label = var_data.get('label', var_id)
                self._add_item_to_list(self.ui.list_equations, var_id, label)
    
    def _add_item_to_list(self, list_widget, var_id, label):
        """
        Add an item to a list widget
        
        Args:
            list_widget: The list widget to add to
            var_id: Variable ID
            label: Variable label
        """
        from PyQt5.QtWidgets import QTreeWidgetItem
        
        # Create tree widget item
        item = QTreeWidgetItem(list_widget)
        item.setText(0, label)
        item.setData(0, 32, var_id)  # Store var_id as user data
        
        # Set tooltip
        item.setToolTip(0, f"ID: {var_id}\nLabel: {label}")
    
    def clear_all_lists(self):
        """Clear all list widgets"""
        lists = [
            self.ui.list_inputs,
            self.ui.list_outputs,
            self.ui.list_instantiate,
            self.ui.list_not_defined_variables,
            self.ui.list_equations
        ]
        
        for list_widget in lists:
            self._safe_clear_list(list_widget)
    
    def _safe_clear_list(self, list_widget):
        """
        Safely clear a list widget
        
        Args:
            list_widget: The list widget to clear
        """
        try:
            list_widget.clear()
        except Exception as e:
            print(f"Error clearing list: {e}")
    
    def refresh_list_widget_settings(self):
        """Refresh settings for all list widgets"""
        self._configure_list_widgets()
    
    def update_entity_type_display(self, entity_type):
        """
        Update the entity type display
        
        Args:
            entity_type: The entity type information
        """
        if entity_type:
            type_name = entity_type.get('name', 'Unknown')
            self.ui.label_entity_type.setText(f"Entity Type: {type_name}")
        else:
            self.ui.label_entity_type.setText("No entity selected")
    
    def update_mode_display(self, mode):
        """
        Update the mode display
        
        Args:
            mode: The current mode
        """
        mode_text = mode.capitalize() if mode else "Normal"
        self.ui.label_mode.setText(f"{mode_text} mode")
    
    def set_accept_button_enabled(self, enabled):
        """
        Enable or disable the accept button
        
        Args:
            enabled: Whether to enable the accept button
        """
        self.ui.pushAccept.setEnabled(enabled)
    
    def set_variable_buttons_enabled(self, enabled):
        """
        Enable or disable variable manipulation buttons
        
        Args:
            enabled: Whether to enable the buttons
        """
        variable_buttons = [
            self.ui.pushAddVariable,
            self.ui.pushAddStateVariable,
            self.ui.pushAddTransport,
            self.ui.pushAddIntensitity,
            self.ui.pushDeleteVariable
        ]
        
        for button in variable_buttons:
            button.setEnabled(enabled)
    
    def get_selected_variable_id(self, list_widget):
        """
        Get the currently selected variable ID from a list widget
        
        Args:
            list_widget: The list widget to get selection from
            
        Returns:
            str: The selected variable ID, or None if no selection
        """
        try:
            current_item = list_widget.currentItem()
            if current_item:
                return current_item.data(0, 32)  # Get var_id from user data
            return None
        except Exception as e:
            print(f"Error getting selected variable ID: {e}")
            return None
    
    def show_status_message(self, message, timeout=3000):
        """
        Show a status message
        
        Args:
            message: The message to show
            timeout: Message timeout in milliseconds
        """
        if hasattr(self.ui, 'statusBar'):
            self.ui.statusBar.showMessage(message, timeout)
        else:
            print(f"Status: {message}")
    
    def confirm_action(self, title, message):
        """
        Show a confirmation dialog
        
        Args:
            title: Dialog title
            message: Dialog message
            
        Returns:
            bool: True if user confirms, False otherwise
        """
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self.parent, title, message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        return reply == QMessageBox.Yes
