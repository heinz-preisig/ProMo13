"""
State Manager for Entity Editor
Ensures consistent Entity state across frontend and backend operations
"""

class EntityStateManager:
    """Manages Entity state with proper lifecycle and validation"""
    
    def __init__(self):
        self._current_entity = None
        self._entity_frontend = None
        self._entity_backend = None
        
    def set_frontend(self, frontend):
        """Set frontend reference"""
        self._entity_frontend = frontend
        
    def set_backend(self, backend):
        """Set backend reference"""
        self._entity_backend = backend
        
    def get_or_create_entity(self, entity_id=None, all_equations=None, var_eq_forest=None, 
                           init_vars=None, input_vars=None, output_vars=None):
        """
        Get current entity or create new one if needed.
        This is the SINGLE SOURCE OF TRUTH for Entity objects.
        """
        print(f"=== STATE MANAGER DEBUG: get_or_create_entity called ===")
        print(f"=== STATE MANAGER DEBUG: entity_id parameter: {entity_id} ===")
        print(f"=== STATE MANAGER DEBUG: current_entity is None: {self._current_entity is None} ===")
        
        if self._current_entity is not None:
            print(f"=== STATE MANAGER DEBUG: Returning existing entity ===")
            return self._current_entity
            
        # Create new entity only if none exists
        if entity_id is None:
            entity_id = "macroscopic.node.mass|constant|infinity.defaultEntity"
            print(f"=== STATE MANAGER DEBUG: Using default entity_id: {entity_id} ===")
            
        from Common.classes.entity_v1 import Entity
        
        print(f"=== STATE MANAGER DEBUG: Creating new Entity with entity_id: {entity_id} ===")
        self._current_entity = Entity(
            entity_id=entity_id,
            all_equations=all_equations or {},
            var_eq_forest=var_eq_forest or [{}],
            init_vars=init_vars or [],
            input_vars=input_vars or [],
            output_vars=output_vars or []
        )
        
        print(f"=== STATE MANAGER DEBUG: Created entity, checking entity_id attribute ===")
        print(f"=== STATE MANAGER DEBUG: hasattr(entity_id): {hasattr(self._current_entity, 'entity_id')} ===")
        if hasattr(self._current_entity, 'entity_id'):
            print(f"=== STATE MANAGER DEBUG: Entity.entity_id after creation: {getattr(self._current_entity, 'entity_id')} ===")
        
        # Update frontend reference
        if self._entity_frontend:
            self._entity_frontend.current_entity = self._current_entity
            self._entity_frontend.current_entity_data = {
                'entity_object': self._current_entity,
                'entity_id': entity_id,
                'entity_name': entity_id
            }
            
        return self._current_entity
        
    def update_entity_state(self, entity):
        """Update the current entity state"""
        if entity != self._current_entity:
            self._current_entity = entity
            
            # Update frontend reference
            if self._entity_frontend:
                self._entity_frontend.current_entity = entity
                self._entity_frontend.current_entity_data = {
                    'entity_object': entity,
                    'entity_id': getattr(entity, 'entity_id', 'unknown'),
                    'entity_name': getattr(entity, 'name', 'unknown')
                }
                
                # IMPORTANT: Refresh UI lists to show updated classifications
                try:
                    self._entity_frontend.populate_lists_from_entity(entity)
                except Exception as e:
                    print(f"Error refreshing UI lists: {e}")
    
    def get_current_entity(self):
        """Get current entity with validation"""
        if self._current_entity is None:
            raise ValueError("No current entity - state not initialized")
        return self._current_entity
    
    def clear_state(self):
        """Clear current entity state"""
        self._current_entity = None
        if self._entity_frontend:
            self._entity_frontend.current_entity = None
            self._entity_frontend.current_entity_data = None

# Global state manager instance
_state_manager = EntityStateManager()

def get_state_manager():
    """Get the global state manager instance"""
    return _state_manager
