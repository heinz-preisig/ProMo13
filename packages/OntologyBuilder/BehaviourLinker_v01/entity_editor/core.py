"""
Entity Editor Core Module
Main coordination module for the Entity Editor
"""

from PyQt5 import QtWidgets
from OntologyBuilder.BehaviourLinker_v01.entity_editor.ui import EntityEditorUI
from OntologyBuilder.BehaviourLinker_v01.entity_editor.data import EntityEditorData
from OntologyBuilder.BehaviourLinker_v01.entity_editor.events import EntityEditorEvents
from OntologyBuilder.BehaviourLinker_v01.entity_editor.classification import EntityEditorClassification


class EntityEditorCore(QtWidgets.QDialog):
    """
    Main Entity Editor dialog - coordinates all components
    """
    
    def __init__(self, parent=None):
        """
        Initialize the Entity Editor
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize components
        self.ui = EntityEditorUI(self)
        self.data = EntityEditorData(self)
        self.events = EntityEditorEvents(self)
        self.classification = EntityEditorClassification(self)
        
        # Initialize state
        self.changed = False
        self.current_entity_data = {}
        
        # Setup initial state
        self._setup_initial_state()
    
    def _setup_initial_state(self):
        """Setup initial dialog state"""
        # Set window properties
        self.setWindowTitle("Entity Editor")
        self.resize(800, 600)
        
        # Setup mode
        self.set_mode("normal")
        
        # Update displays
        self.update_displays()
    
    def set_ontology_container(self, ontology_container):
        """
        Set the ontology container
        
        Args:
            ontology_container: The ontology container object
        """
        self.data.set_ontology_container(ontology_container)
    
    def set_selected_entity_type(self, entity_type):
        """
        Set the selected entity type
        
        Args:
            entity_type: Dictionary containing entity type information
        """
        self.data.set_selected_entity_type(entity_type)
        self.current_entity_data = entity_type or {}
        self.ui.update_entity_type_display(entity_type)
    
    def set_mode(self, mode):
        """
        Set the current mode
        
        Args:
            mode: The mode string
        """
        self.data.set_mode(mode)
        self.ui.update_mode_display(mode)
        self._configure_buttons_for_mode(mode)
    
    def set_entity_object(self, entity):
        """
        Set the current entity object
        
        Args:
            entity: The entity object
        """
        self.data.set_entity_object(entity)
        
        # Populate UI with entity data
        if entity:
            self.ui.populate_lists_from_entity(entity)
    
    def _configure_buttons_for_mode(self, mode):
        """
        Configure buttons based on current mode
        
        Args:
            mode: The current mode
        """
        if mode == "reservoir":
            # Reservoir mode specific configurations
            self.ui.set_variable_buttons_enabled(True)
        else:
            # Normal mode configurations
            self.ui.set_variable_buttons_enabled(bool(self.data.current_entity))
    
    def _update_mode_based_on_selection(self):
        """Update mode based on current selection"""
        # This would update mode based on user selection
        pass
    
    def update_displays(self):
        """Update all display elements"""
        self.ui.update_entity_type_display(self.data.selected_entity_type)
        self.ui.update_mode_display(self.data.mode)
    
    def update_accept_button_visibility(self):
        """Update accept button visibility"""
        if self.changed:
            self.ui.set_accept_button_enabled(True)
        else:
            self.ui.set_accept_button_enabled(False)
    
    def populate_entity_structure(self):
        """Populate entity structure information"""
        # This would populate entity structure in the UI
        pass
    
    def populate_with_entity_data(self, entity_data):
        """
        Populate UI with entity data
        
        Args:
            entity_data: Entity data dictionary
        """
        self.data.process_entity_update(entity_data)
    
    def clear_all_lists(self):
        """Clear all list widgets"""
        self.ui.clear_all_lists()
    
    def safe_clear_list(self, list_widget):
        """
        Safely clear a list widget
        
        Args:
            list_widget: The list widget to clear
        """
        self.ui._safe_clear_list(list_widget)
    
    def add_to_list(self, list_widget, item_id, item_label, item_type="variable"):
        """
        Add an item to a list widget
        
        Args:
            list_widget: The list widget to add to
            item_id: Item ID
            item_label: Item label
            item_type: Type of item
        """
        self.data.add_to_list(list_widget, item_id, item_label, item_type)
    
    def add_variable_to_list(self, list_widget, var_id, var_label=None):
        """
        Add a variable to a list widget
        
        Args:
            list_widget: The list widget to add to
            var_id: Variable ID
            var_label: Variable label
        """
        self.data.add_variable_to_list(list_widget, var_id, var_label)
    
    def add_port_to_list(self, list_widget, port_id, port_label=None):
        """
        Add a port to a list widget
        
        Args:
            list_widget: The list widget to add to
            port_id: Port ID
            port_label: Port label
        """
        self.data.add_port_to_list(list_widget, port_id, port_label)
    
    def populate_lists_from_entity(self, entity):
        """
        Populate all lists from entity data
        
        Args:
            entity: The entity object
        """
        self.ui.populate_lists_from_entity(entity)
    
    def refresh_list_widget_settings(self):
        """Refresh settings for all list widgets"""
        self.ui.refresh_list_widget_settings()
    
    def get_selected_variable_id(self, list_widget):
        """
        Get the currently selected variable ID
        
        Args:
            list_widget: The list widget to get selection from
            
        Returns:
            str: The selected variable ID
        """
        return self.ui.get_selected_variable_id(list_widget)
    
    def update_entity_from_backend_entity(self, backend_entity):
        """
        Update entity from backend entity
        
        Args:
            backend_entity: Backend entity object
        """
        self.data.update_entity_from_backend_entity(backend_entity)
    
    def update_entity_from_backend_new(self, backend_entity):
        """
        Update entity using new backend format
        
        Args:
            backend_entity: Backend entity in new format
        """
        self.data.update_entity_from_backend_new(backend_entity)
    
    def populate_from_entity_data_fallback(self, entity_data):
        """
        Fallback method to populate from entity data
        
        Args:
            entity_data: Entity data dictionary
        """
        self.data.populate_from_entity_data_fallback(entity_data)
    
    def launch_equation_editor(self):
        """Launch the equation editor"""
        # This would launch the equation editor dialog
        pass
    
    def launch_state_variable_selector(self):
        """Launch state variable selector"""
        # This would launch the state variable selector dialog
        pass
    
    def launch_new_variable_selector(self):
        """Launch new variable selector"""
        # This would launch the new variable selector dialog
        pass
    
    def launch_behavior_association_editor(self):
        """Launch behavior association editor"""
        # This would launch the behavior association editor dialog
        pass
    
    def handle_state_variable_selection(self, selected_variables):
        """
        Handle state variable selection
        
        Args:
            selected_variables: List of selected variables
        """
        # Process selected state variables
        pass
    
    def handle_new_variable_addition(self, variable_data):
        """
        Handle new variable addition
        
        Args:
            variable_data: Variable data dictionary
        """
        # Process new variable addition
        pass
    
    def delete_variable_from_context(self, var_id):
        """
        Delete variable from current context
        
        Args:
            var_id: Variable ID to delete
        """
        if self.data.current_entity:
            self.data.current_entity.remove_variable(var_id)
            self.ui.populate_lists_from_entity(self.data.current_entity)
    
    def open_context_menu_directly(self, sender, index, var_id, var_label, var_network, list_name):
        """
        Open context menu directly
        
        Args:
            sender: The sender widget
            index: Model index
            var_id: Variable ID
            var_label: Variable label
            var_network: Variable network
            list_name: List name
        """
        # Create and show context menu
        self.events._create_context_menu(var_id, var_label, list_name, sender, sender.mapToGlobal(sender.pos()))
    
    def markChanged(self):
        """Mark the dialog as changed"""
        self.changed = True
        self.update_accept_button_visibility()
    
    def markSaved(self):
        """Mark the dialog as saved"""
        self.changed = False
        self.update_accept_button_visibility()
    
    def closeMe(self):
        """Close the dialog"""
        self.close()
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        super().mouseMoveEvent(event)
    
    def on_ok(self):
        """Handle OK button press"""
        self.on_pushAccept_pressed()
    
    def on_cancel(self):
        """Handle Cancel button press"""
        self.on_pushCancle_pressed()
    
    def on_pushAccept_pressed(self):
        """Handle Accept button press"""
        # Delegate to events module
        self.events.on_pushAccept_pressed()
    
    def on_pushCancle_pressed(self):
        """Handle Cancel button press"""
        # Delegate to events module
        self.events.on_pushCancle_pressed()
    
    def get_entity_summary(self):
        """
        Get a summary of the current entity
        
        Returns:
            dict: Entity summary
        """
        return self.data.get_entity_summary()
    
    def export_entity_data(self):
        """
        Export entity data for saving
        
        Returns:
            dict: Exportable entity data
        """
        return self.data.export_entity_data()
    
    def import_entity_data(self, entity_data):
        """
        Import entity data from saved state
        
        Args:
            entity_data: Dictionary of entity data
        """
        self.data.import_entity_data(entity_data)
        self.update_displays()
    
    def validate_entity_data(self):
        """
        Validate the current entity data
        
        Returns:
            tuple: (is_valid, error_messages)
        """
        return self.data.validate_entity_data()
    
    def show_status_message(self, message, timeout=3000):
        """
        Show a status message
        
        Args:
            message: The message to show
            timeout: Message timeout in milliseconds
        """
        self.ui.show_status_message(message, timeout)
    
    def confirm_action(self, title, message):
        """
        Show a confirmation dialog
        
        Args:
            title: Dialog title
            message: Dialog message
            
        Returns:
            bool: True if user confirms, False otherwise
        """
        return self.ui.confirm_action(title, message)
    
    def get_classification_summary(self):
        """
        Get classification summary
        
        Returns:
            dict: Classification summary
        """
        return self.classification.get_classification_summary()
    
    def validate_classifications(self):
        """
        Validate all classifications
        
        Returns:
            tuple: (is_valid, validation_results)
        """
        return self.classification.validate_classifications()
    
    def export_classifications(self):
        """
        Export classifications for saving
        
        Returns:
            dict: Exportable classification data
        """
        return self.classification.export_classifications()
    
    def import_classifications(self, classification_data):
        """
        Import classifications from saved state
        
        Args:
            classification_data: Dictionary of classification data
        """
        self.classification.import_classifications(classification_data)
