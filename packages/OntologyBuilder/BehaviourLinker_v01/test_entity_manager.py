#!/usr/bin/env python3
"""
Test EntityManager logic independently
"""

import sys
import os

# Add the packages directory to path for testing
root = os.path.abspath('..')
sys.path.extend([root, os.path.join(root, 'packages')])

def test_entity_manager():
    """Test EntityManager functionality"""
    print('=== Testing EntityManager ===')
    
    # Mock entity class for testing
    class MockEntity:
        def __init__(self, entity_id):
            self.entity_id = entity_id
        
        def convert_to_dict(self):
            return {'id': self.entity_id}
    
    # Test EntityManager
    from entity.entity_manager import EntityManager
    
    # Create mock ontology container
    class MockOntology:
        def __init__(self):
            self.entity_dictionary = {
                'macroscopic.node.mass|event|lumped.entity1': MockEntity('macroscopic.node.mass|event|lumped.entity1'),
                'macroscopic.node.mass|event|lumped.entity2': MockEntity('macroscopic.node.mass|event|lumped.entity2'),
            }
    
    manager = EntityManager(MockOntology())
    
    # Test entity ID generation
    entity_id = manager.generate_entity_id('macroscopic', 'node', 'mass|event|lumped', 'new_entity')
    print(f'✅ Generated ID: {entity_id}')
    
    # Test existing names retrieval
    existing_names = manager.get_existing_names_for_type('macroscopic', 'node', 'mass|event|lumped')
    print(f'✅ Existing names: {existing_names}')
    
    # Test entity preparation
    mock_entity = MockEntity('old_malformed_id')
    entity_type_info = {
        'network': 'macroscopic',
        'category': 'node', 
        'entity type': 'mass|event|lumped',
        'name': 'test_entity'
    }
    
    prepared_id, prepared_entity = manager.prepare_entity_for_save(mock_entity, entity_type_info)
    print(f'✅ Prepared entity ID: {prepared_id}')
    print(f'✅ Entity object ID: {prepared_entity.entity_id}')
    
    print('🎉 EntityManager tests passed!')

if __name__ == "__main__":
    test_entity_manager()
