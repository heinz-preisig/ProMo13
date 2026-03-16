"""
Entity Editor Data Module
Handles all data operations, entity management, and ontology operations
"""


class EntityEditorData:
    """
    Manages all data operations for the Entity Editor
    """
    
    def __init__(self, parent_dialog):
        """
        Initialize the data manager
        
        Args:
            parent_dialog: The parent EntityEditorCore dialog
        """
        self.parent = parent_dialog
        self.ontology_container = None
        self.current_entity = None
        self.selected_entity_type = None
        self.mode = "normal"
    
    def set_ontology_container(self, ontology_container):
        """
        Set the ontology container for variable data access
        
        Args:
            ontology_container: The ontology container object
        """
        self.ontology_container = ontology_container
    
    def set_selected_entity_type(self, entity_type):
        """
        Set the selected entity type
        
        Args:
            entity_type: Dictionary containing entity type information
        """
        self.selected_entity_type = entity_type
    
    def set_entity_object(self, entity):
        """
        Set the current entity object
        
        Args:
            entity: The entity object
        """
        self.current_entity = entity
    
    def set_mode(self, mode):
        """
        Set the current mode
        
        Args:
            mode: The mode string (e.g., "normal", "reservoir")
        """
        self.mode = mode
    
    def get_entity_domain(self):
        """
        Get the domain branch for the current entity
        
        Returns:
            str: Domain branch (physical, control, info_processing, reaction)
        """
        if self.selected_entity_type:
            return self.selected_entity_type.get('network', 'physical')
        return 'physical'  # Default to physical
    
    def get_variable_info(self, var_id):
        """
        Get information about a variable
        
        Args:
            var_id: Variable ID
            
        Returns:
            dict: Variable information
        """
        var_info = {'id': var_id, 'type': 'unknown', 'label': var_id}
        
        if self.ontology_container:
            variables = getattr(self.ontology_container, 'variables', {})
            if var_id in variables:
                var_data = variables[var_id]
                var_info.update({
                    'label': var_data.get('label', var_id),
                    'type': var_data.get('type', 'unknown'),
                    'description': var_data.get('description', ''),
                    'network': var_data.get('network', 'unknown')
                })
        
        return var_info
    
    def get_current_classification_for_variable(self, var_id):
        """
        Get current classification for a variable
        
        Args:
            var_id: Variable ID
            
        Returns:
            list: Current classifications
        """
        if self.current_entity:
            manual_classifications = getattr(self.current_entity, 'local_variable_classifications', {})
            var_class_info = manual_classifications.get(var_id, {})
            current_classifications = var_class_info.get('classification', ['none'])
            
            if isinstance(current_classifications, list) and current_classifications:
                return current_classifications
            return current_classifications or ['none']
        return ['none']
    
    def add_variable_to_list(self, list_widget, var_id, var_label=None):
        """
        Add a variable to a list widget
        
        Args:
            list_widget: The list widget to add to
            var_id: Variable ID
            var_label: Variable label (optional)
        """
        from PyQt5.QtWidgets import QTreeWidgetItem
        
        if not var_label:
            var_info = self.get_variable_info(var_id)
            var_label = var_info.get('label', var_id)
        
        # Create tree widget item
        item = QTreeWidgetItem(list_widget)
        item.setText(0, var_label)
        item.setData(0, 32, var_id)  # Store var_id as user data
        
        # Set tooltip
        item.setToolTip(0, f"ID: {var_id}\nLabel: {var_label}")
    
    def add_port_to_list(self, list_widget, port_id, port_label=None):
        """
        Add a port to a list widget
        
        Args:
            list_widget: The list widget to add to
            port_id: Port ID
            port_label: Port label (optional)
        """
        from PyQt5.QtWidgets import QTreeWidgetItem
        
        if not port_label:
            port_label = port_id
        
        # Create tree widget item
        item = QTreeWidgetItem(list_widget)
        item.setText(0, port_label)
        item.setData(0, 32, port_id)  # Store port_id as user data
        
        # Set tooltip
        item.setToolTip(0, f"Port ID: {port_id}\nLabel: {port_label}")
    
    def add_to_list(self, list_widget, item_id, item_label, item_type="variable"):
        """
        Generic method to add an item to a list widget
        
        Args:
            list_widget: The list widget to add to
            item_id: Item ID
            item_label: Item label
            item_type: Type of item (for tooltip)
        """
        from PyQt5.QtWidgets import QTreeWidgetItem
        
        # Create tree widget item
        item = QTreeWidgetItem(list_widget)
        item.setText(0, item_label)
        item.setData(0, 32, item_id)  # Store item_id as user data
        
        # Set tooltip
        item.setToolTip(0, f"{item_type.capitalize()} ID: {item_id}\nLabel: {item_label}")
    
    def process_entity_update(self, entity_data):
        """
        Process entity data updates
        
        Args:
            entity_data: Updated entity data
        """
        if self.current_entity:
            # Update entity with new data
            for key, value in entity_data.items():
                if hasattr(self.current_entity, key):
                    setattr(self.current_entity, key, value)
            
            # Trigger UI refresh
            if hasattr(self.parent, 'ui') and self.parent.ui:
                self.parent.ui.populate_lists_from_entity(self.current_entity)
    
    def update_entity_from_backend_entity(self, backend_entity):
        """
        Update the current entity from a backend entity
        
        Args:
            backend_entity: Backend entity object
        """
        if backend_entity and self.current_entity:
            # Copy relevant attributes
            attributes_to_copy = [
                'name', 'entity_type', 'variables', 'classifications',
                'local_variable_classifications', 'state_variables'
            ]
            
            for attr in attributes_to_copy:
                if hasattr(backend_entity, attr):
                    setattr(self.current_entity, attr, getattr(backend_entity, attr))
    
    def update_entity_from_backend_new(self, backend_entity):
        """
        Update entity using new backend format
        
        Args:
            backend_entity: Backend entity in new format
        """
        if backend_entity and self.current_entity:
            # Handle new backend entity format
            if isinstance(backend_entity, dict):
                for key, value in backend_entity.items():
                    setattr(self.current_entity, key, value)
            else:
                # Handle object format
                self.update_entity_from_backend_entity(backend_entity)
    
    def populate_from_entity_data_fallback(self, entity_data):
        """
        Fallback method to populate from entity data
        
        Args:
            entity_data: Entity data dictionary
        """
        if entity_data and hasattr(self.parent, 'ui'):
            # Try to populate lists using available data
            variables = entity_data.get('variables', {})
            
            for var_id, var_data in variables.items():
                var_label = var_data.get('label', var_id)
                var_classification = var_data.get('classification', ['none'])
                
                # Add to appropriate list based on classification
                if 'input' in var_classification:
                    self.parent.ui.add_variable_to_list(self.parent.ui.list_inputs, var_id, var_label)
                elif 'output' in var_classification:
                    self.parent.ui.add_variable_to_list(self.parent.ui.list_outputs, var_id, var_label)
                elif 'instantiate' in var_classification:
                    self.parent.ui.add_variable_to_list(self.parent.ui.list_instantiate, var_id, var_label)
                else:
                    self.parent.ui.add_variable_to_list(self.parent.ui.list_not_defined_variables, var_id, var_label)
    
    def validate_entity_data(self):
        """
        Validate the current entity data
        
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        if not self.current_entity:
            errors.append("No entity object set")
            return False, errors
        
        if not self.ontology_container:
            errors.append("No ontology container set")
            return False, errors
        
        # Validate required fields
        if not hasattr(self.current_entity, 'name') or not self.current_entity.name:
            errors.append("Entity name is required")
        
        if not hasattr(self.current_entity, 'entity_type'):
            errors.append("Entity type is required")
        
        # Validate variable classifications
        if hasattr(self.current_entity, 'local_variable_classifications'):
            classifications = self.current_entity.local_variable_classifications
            for var_id, var_class in classifications.items():
                if not var_class.get('classification'):
                    errors.append(f"Variable {var_id} has no classification")
        
        return len(errors) == 0, errors
    
    def get_entity_summary(self):
        """
        Get a summary of the current entity
        
        Returns:
            dict: Entity summary information
        """
        summary = {
            'name': getattr(self.current_entity, 'name', 'Unknown'),
            'type': getattr(self.current_entity, 'entity_type', 'Unknown'),
            'domain': self.get_entity_domain(),
            'mode': self.mode,
            'variable_count': 0,
            'classification_count': 0
        }
        
        if self.current_entity:
            # Count variables
            if hasattr(self.current_entity, 'local_variable_classifications'):
                summary['classification_count'] = len(self.current_entity.local_variable_classifications)
            
            if self.ontology_container and hasattr(self.ontology_container, 'variables'):
                summary['variable_count'] = len(self.ontology_container.variables)
        
        return summary
    
    def export_entity_data(self):
        """
        Export entity data for saving
        
        Returns:
            dict: Exportable entity data
        """
        if not self.current_entity:
            return {}
        
        export_data = {
            'name': getattr(self.current_entity, 'name', ''),
            'entity_type': getattr(self.current_entity, 'entity_type', ''),
            'domain': self.get_entity_domain(),
            'mode': self.mode,
            'local_variable_classifications': getattr(self.current_entity, 'local_variable_classifications', {}),
            'state_variables': getattr(self.current_entity, 'state_variables', []),
            'classifications_initialized': getattr(self.current_entity, 'classifications_initialized', False)
        }
        
        return export_data
    
    def import_entity_data(self, entity_data):
        """
        Import entity data from saved state
        
        Args:
            entity_data: Dictionary of entity data to import
        """
        if not entity_data:
            return
        
        # Set basic attributes
        if 'mode' in entity_data:
            self.set_mode(entity_data['mode'])
        
        if 'domain' in entity_data:
            # Update selected entity type with domain info
            if self.selected_entity_type:
                self.selected_entity_type['network'] = entity_data['domain']
        
        # Update current entity if it exists
        if self.current_entity:
            for key, value in entity_data.items():
                if hasattr(self.current_entity, key) or key in ['name', 'entity_type', 'local_variable_classifications']:
                    setattr(self.current_entity, key, value)
