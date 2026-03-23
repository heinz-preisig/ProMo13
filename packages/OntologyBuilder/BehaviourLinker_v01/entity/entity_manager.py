#!/usr/bin/env python3
"""
Simple Entity Manager - Extracted from complex entity handling logic
Minimal refactoring to fix entity creation and saving issues
"""

import copy


class EntityManager:
    """Simple manager for entity creation and ID handling"""
    
    def __init__(self, ontology_container):
        self.ontology_container = ontology_container
        self.existing_entities = {}
        
    def generate_entity_id(self, network, category, entity_type, name):
        """Generate proper entity ID with all 4 parts"""
        if not name:
            # Generate default name if none provided
            existing_names = self.get_existing_names_for_type(network, category, entity_type)
            counter = 1
            while f"{entity_type}_{counter}" in existing_names:
                counter += 1
            name = f"{entity_type}_{counter}"
        
        return f"{network}.{category}.{entity_type}.{name}"
    
    def get_existing_names_for_type(self, network, category, entity_type):
        """Get all existing entity names for a specific entity type"""
        existing_names = []
        
        try:
            # Get all entities from ontology container
            all_entities = getattr(self.ontology_container, 'entity_dictionary', {})
            
            for entity_id in all_entities:
                if ">" not in entity_id:  # Skip arc entities
                    parts = entity_id.split('.')
                    if len(parts) == 4:
                        entity_net, entity_cat, entity_type_name, entity_name = parts
                        
                        # Check if this entity matches the requested type
                        if (entity_net == network and
                            entity_cat == category and
                            entity_type_name == entity_type):
                            existing_names.append(entity_name)
            
            return existing_names
            
        except Exception as e:
            print(f"ERROR getting existing names: {e}")
            return []
    
    def create_entity_with_proper_id(self, entity_type_info, entity_object):
        """Create entity with proper ID and avoid duplicates"""
        network = entity_type_info.get('network', 'macroscopic')
        category = entity_type_info.get('category', 'node')
        entity_type = entity_type_info.get('entity type', 'unknown')
        name = entity_type_info.get('name')
        
        # Generate proper entity ID
        entity_id = self.generate_entity_id(network, category, entity_type, name)
        
        # Update the entity object with the correct ID
        if hasattr(entity_object, 'entity_id'):
            entity_object.entity_id = entity_id
        
        print(f"=== ENTITY MANAGER: Created entity with ID: {entity_id} ===")
        
        return entity_id, entity_object
    
    def prepare_entity_for_save(self, entity, entity_type_info):
        """Prepare entity for saving with correct ID format"""
        # Ensure entity has proper ID
        if not hasattr(entity, 'entity_id') or not entity.entity_id:
            entity_id, entity = self.create_entity_with_proper_id(entity_type_info, entity)
            return entity_id, entity
        
        # If entity already has ID, make sure it's properly formatted
        entity_id = entity.entity_id
        if "." not in entity_id or len(entity_id.split(".")) != 4:
            # Fix malformed entity ID
            network = entity_type_info.get('network', 'macroscopic')
            category = entity_type_info.get('category', 'node')
            entity_type = entity_type_info.get('entity type', 'unknown')
            name = entity_type_info.get('name', 'default_entity')
            
            entity_id = self.generate_entity_id(network, category, entity_type, name)
            entity.entity_id = entity_id
            
            print(f"=== ENTITY MANAGER: Fixed malformed ID from {entity.entity_id} to {entity_id} ===")
        
        return entity_id, entity
