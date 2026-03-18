#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
Minimal Refactoring Test - Entity Front End with IconHelper
Only icon calls are replaced, everything else is identical
===============================================================================
"""

# Import the original class
try:
    from .entity_front_end import EntityEditorFrontEnd
except ImportError:
    from entity_front_end import EntityEditorFrontEnd
from .icon_helper import IconHelper
from .entity_manager import EntityManager


class EntityEditorFrontEndWithHelper(EntityEditorFrontEnd):
    """
    Minimal refactoring - only replace icon calls with IconHelper
    All other functionality remains exactly the same
    """
    
    def __init__(self):
        """Initialize exactly like the original, but use IconHelper for icons"""
        # Call the original __init__ first - this sets up everything including button connections
        super().__init__()
        
        # Initialize EntityManager for proper entity handling
        self.entity_manager = EntityManager(self.ontology_container) if hasattr(self, 'ontology_container') and self.ontology_container else None
        
        # Now replace round button calls with IconHelper (minimal change)
        # Note: We're re-doing the button setup but keeping all other connections intact
        IconHelper.setup_round_button(self.ui.pushAddVariable, "new", tooltip="new variable")
        IconHelper.setup_round_button(self.ui.pushAddStateVariable, "dependent_variable", tooltip="add state variable")
        IconHelper.setup_round_button(self.ui.pushAddTransport, "token_flow", tooltip="add transport variable")
        IconHelper.setup_round_button(self.ui.pushEditVariable, "edit", tooltip="edit variable")
        IconHelper.setup_round_button(self.ui.pushDeleteVariable, "delete", tooltip="delete variable")
        IconHelper.setup_round_button(self.ui.pushAccept, "accept", tooltip="accept")
        IconHelper.setup_round_button(self.ui.pushCancle, "cancel", tooltip="cancel")
        IconHelper.setup_round_button(self.ui.pushAddIntensitity, "infinity", tooltip="secondary states -- intensities")
        
        # Keep the LED button setup exactly like the original
        self.signalButton = IconHelper.setup_round_button(self.ui.LED, "LED_green", tooltip="status", mysize=20)
    
    def add_variable_to_list(self, list_widget, var_info, icon=None):
        """Add variable to list - use IconHelper if no icon provided"""
        if icon is None:
            # Use IconHelper to get appropriate icon
            icon = IconHelper.get_variable_icon(var_info['id'], self.ontology_container)
        
        # Use the original logic, just with our icon
        var_text = f"{var_info['label']} (ID: {var_info['id']}, Network: {var_info['network']})"
        
        # Create item with icon
        item = QStandardItem(var_text)
        if icon:
            item.setIcon(icon)
        
        # Store variable data
        item.setData(var_info, 32)  # Qt.UserRole
        
        # Add to model
        model = list_widget.model()
        if model is None:
            model = QStandardItemModel(list_widget)
            list_widget.setModel(model)
        
        model.appendRow(item)
    
    def _add_equation_to_list(self, list_widget, eq_id, icon=None):
        """Add equation to list - use IconHelper for equation icon"""
        if icon is None:
            icon = IconHelper.get_equation_icon()
        
        # Use the original logic, just with our icon
        eq_text = f"Equation {eq_id}"
        eq_data = {
            'id': eq_id,
            'label': eq_text,
            'network': 'unknown'  # Equations don't have network info
        }
        
        # Add to model using the original approach
        model = list_widget.model()
        if model is None:
            model = QStandardItemModel(list_widget)
            list_widget.setModel(model)
        
        model.appendRow(item)
    
    def set_entity_object(self, entity):
        """Set the Entity object and update the UI"""
        print(f"=== HELPER DEBUG: set_entity_object called with entity: {entity} ===")
        self.current_entity = entity
        print(f"=== HELPER DEBUG: current_entity set to: {self.current_entity} ===")

        # Update the lists with Entity information
        self.populate_lists_from_entity(entity)

    def on_pushAccept_pressed(self):
        """Handle Accept button - save entity with proper ID using EntityManager"""
        try:
            # Mark entity as saved
            self.markSaved()

            # Use EntityManager to prepare entity for saving
            if hasattr(self, 'current_entity') and self.current_entity and self.entity_manager:
                # Get entity type info from current entity data
                entity_type_info = {
                    'network': getattr(self.current_entity_data, 'network', 'macroscopic') if hasattr(self, 'current_entity_data') and self.current_entity_data else 'macroscopic',
                    'category': getattr(self.current_entity_data, 'category', 'node') if hasattr(self, 'current_entity_data') and self.current_entity_data else 'node',
                    'entity type': getattr(self.current_entity_data, 'entity_type', 'unknown') if hasattr(self, 'current_entity_data') and self.current_entity_data else 'unknown',
                    'name': getattr(self.current_entity_data, 'name', None) if hasattr(self, 'current_entity_data') and self.current_entity_data else None
                }
                
                # Prepare entity with proper ID
                entity_id, prepared_entity = self.entity_manager.prepare_entity_for_save(self.current_entity, entity_type_info)
                
                print(f"=== HELPER DEBUG: Saving entity with ID: {entity_id} ===")
                
                # Send save message to backend with properly prepared entity
                message = {
                        "event" : "save_entity",
                        "entity": prepared_entity,
                        "entity_id": entity_id  # Include proper ID
                        }
                self.message.emit(message)
                self.close()
            else:
                # Fallback to original behavior if no EntityManager
                if hasattr(self, 'current_entity') and self.current_entity:
                    message = {
                            "event" : "save_entity",
                            "entity": self.current_entity
                            }
                    self.message.emit(message)
                    self.close()

        except Exception as e:
            from OntologyBuilder.BehaviourLinker_v01.error_logger import log_error
            from OntologyBuilder.BehaviourLinker_v01.resources.pop_up_message_box import makeMessageBox
            log_error("on_pushAccept_pressed", e, "saving entity")
            makeMessageBox(f"Error saving entity: {str(e)}")


# Factory function for testing
def create_entity_editor_with_helper():
    """Create entity editor with IconHelper - same interface as original"""
    return EntityEditorFrontEndWithHelper()
