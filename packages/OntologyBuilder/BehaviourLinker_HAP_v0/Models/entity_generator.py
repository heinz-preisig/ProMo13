from typing import List, Optional, Dict, Any
import itertools

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QStringListModel, QObject, pyqtSignal
from Common.classes import ontology
from OntologyBuilder.BehaviourLinker_HAP_v0.Models import tree_bases


class EntityGenerator(QObject):
    """Handles generation of entities based on entity types."""
    
    # Signal emitted when entities are generated
    entities_generated = pyqtSignal(list)
    
    def __init__(self, ontology_container):
        super().__init__()
        self.ontology_container = ontology_container
        
    def get_tokens_for_entity_type(self, network, entity_class, mechanism, nature):
        """Get all valid tokens for the given entity type.
        
        Args:
            network: The network name
            entity_class: The entity class (constant, dynamic, event)
            mechanism: The mechanism (AE, ODE, lumped, distributed, infinity)
            nature: The nature (signal, charge, energy, mass, species)
            
        Returns:
            list: List of valid tokens for the entity type
        """
        tokens = set()
        
        # Get tokens from the ontology container
        if hasattr(self.ontology_container, 'get_tokens'):
            tokens.update(self.ontology_container.get_tokens(network))
            
        # If no tokens found, return a default token
        if not tokens:
            tokens.add('default')
            
        return sorted(tokens)
        
    def generate_entity(self, network, entity_class, mechanism, nature, token):
        """Generate an entity with the given parameters.
        
        Args:
            network: The network name
            entity_class: The entity class (constant, dynamic, event)
            mechanism: The mechanism (AE, ODE, lumped, distributed, infinity)
            nature: The nature (signal, charge, energy, mass, species)
            token: The token for the entity
            
        Returns:
            dict: The generated entity
        """
        # Generate a unique ID for the entity
        entity_id = f"{network}.{entity_class}|{mechanism}|{nature}|{token}"
        
        # Create the entity dictionary
        entity = {
            'id': entity_id,
            'network': network,
            'class': entity_class,
            'mechanism': mechanism,
            'nature': nature,
            'token': token,
            'properties': self._get_default_properties(entity_class, mechanism, nature)
        }
        
        return entity
        
    def _get_default_properties(self, entity_class, mechanism, nature):
        """Get default properties for the entity type."""
        properties = {}
        
        # Set class-specific properties
        if entity_class == 'constant':
            properties['is_constant'] = True
        elif entity_class == 'dynamic':
            properties['is_dynamic'] = True
        elif entity_class == 'event':
            properties['is_event'] = True
            
        # Add mechanism-specific properties
        if mechanism == 'lumped':
            properties['is_lumped'] = True
        elif mechanism == 'distributed':
            properties['is_distributed'] = True
        elif mechanism == 'ODE':
            properties['is_ode'] = True
            
        # Add nature-specific properties
        if nature == 'charge':
            properties['unit'] = 'C'
        elif nature == 'energy':
            properties['unit'] = 'J'
        elif nature == 'mass':
            properties['unit'] = 'kg'
        elif nature == 'species':
            properties['is_species'] = True
            
        return properties

    def add_entity_name(self, name: str):
        """Add a name to create a new entity ID.
        
        Args:
            name: The name to use for the new entity
            
        Returns:
            str: The generated entity ID
        """
        # This method would be part of the EntityGenerator class
        # and would generate a new entity ID based on the current context
        return f"generated_entity_{name}"  # Placeholder implementation
