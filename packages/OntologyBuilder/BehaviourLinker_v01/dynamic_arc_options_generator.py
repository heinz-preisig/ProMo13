#!/usr/local/bin/python3
# encoding: utf-8

"""
Dynamic arc options generator that extracts effort variable mappings from ontology
Fully dynamic system that adapts to any ontology structure
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path


class DynamicPhysicalDomainMapper:
    """
    Dynamically generates physical domain mappings from ontology and entity definitions
    """
    
    def __init__(self, ontology_data: Dict[str, Any], entities_data: Dict[str, Any]):
        """
        Initialize with ontology and entities data
        
        Args:
            ontology_data: Ontology structure from ontology.json
            entities_data: Entity definitions with variables
        """
        self.ontology = ontology_data
        self.entities = entities_data
        self.effort_variable_mappings = self._extract_effort_variable_mappings()
        self.transport_equations = self._extract_transport_equations()
    
    def _extract_effort_variable_mappings(self) -> Dict[str, Dict[str, str]]:
        """
        Dynamically extract effort variable mappings from entities
        
        Returns:
            Dictionary mapping token|mechanism to physical domain info
        """
        mappings = {}
        
        # Look for arc entities and extract their effort variables
        for entity_name, entity_data in self.entities.items():
            if self._is_arc_entity(entity_name, entity_data):
                token_mechanism = self._extract_token_mechanism(entity_name)
                if token_mechanism:
                    effort_var = self._find_effort_variable(entity_data)
                    if effort_var:
                        mappings[token_mechanism] = {
                            "effort_variable": effort_var,
                            "token": token_mechanism.split('|')[0],
                            "transport_equation": token_mechanism.split('|')[1],
                            "flow_variable": self._infer_flow_variable(token_mechanism, entity_data)
                        }
        
        return mappings
    
    def _is_arc_entity(self, entity_name: str, entity_data: Dict[str, Any]) -> bool:
        """Check if entity is an arc entity"""
        # Check naming convention
        if ".arc." in entity_name:
            return True
        
        # Check entity type if available
        if hasattr(entity_data, 'get_type') and entity_data.get_type() == "arc":
            return True
            
        # Check structure
        if isinstance(entity_data, dict):
            if "entity_type" in entity_data and entity_data["entity_type"] == "arc":
                return True
        
        return False
    
    def _extract_token_mechanism(self, entity_name: str) -> Optional[str]:
        """
        Extract token|mechanism from entity name
        
        Example: "macroscopic.arc.mass|convection|lumped.convectiveMassFlow" 
        Returns: "mass|convection"
        """
        try:
            parts = entity_name.split('.')
            if len(parts) >= 3:
                token_mechanism_part = parts[2]
                if '|' in token_mechanism_part:
                    return token_mechanism_part
        except (IndexError, AttributeError):
            pass
        return None
    
    def _find_effort_variable(self, entity_data: Dict[str, Any]) -> Optional[str]:
        """
        Find the effort variable for an arc entity
        
        Args:
            entity_data: Entity definition data
            
        Returns:
            Name of effort variable or None if not found
        """
        # Look for variables marked as 'effort' type
        if hasattr(entity_data, 'get_variables'):
            variables = entity_data.get_variables()
            for var in variables:
                if hasattr(var, 'get_type') and var.get_type() == 'effort':
                    return var.get_name()
        
        # Look in dictionary structure
        if isinstance(entity_data, dict):
            variables = entity_data.get('variables', {})
            for var_name, var_data in variables.items():
                if isinstance(var_data, dict) and var_data.get('type') == 'effort':
                    return var_name
                
                # Check variable classification
                if 'classification' in var_data and var_data['classification'] == 'effort':
                    return var_name
        
        # Fallback: infer from entity type and naming
        return self._infer_effort_variable_fallback(entity_data)
    
    def _infer_effort_variable_fallback(self, entity_data: Dict[str, Any]) -> Optional[str]:
        """
        Fallback method to infer effort variable from entity characteristics
        
        Args:
            entity_data: Entity definition data
            
        Returns:
            Inferred effort variable name
        """
        # Extract from entity name or type
        entity_name = entity_data.get('name', str(entity_data))
        
        # Mass transport
        if 'mass' in entity_name.lower():
            if 'convection' in entity_name.lower():
                return 'pressure'
            elif 'diffusion' in entity_name.lower():
                return 'chemical_potential'
        
        # Energy transport  
        if 'energy' in entity_name.lower() or 'heat' in entity_name.lower():
            return 'temperature'
        
        # Charge transport
        if 'charge' in entity_name.lower() or 'electric' in entity_name.lower():
            return 'voltage'
        
        # Momentum transport
        if 'momentum' in entity_name.lower():
            if 'convection' in entity_name.lower():
                return 'velocity'
            elif 'diffusion' in entity_name.lower():
                return 'stress'
        
        return None
    
    def _infer_flow_variable(self, token_mechanism: str, entity_data: Dict[str, Any]) -> str:
        """
        Infer flow variable name from token and mechanism
        
        Args:
            token_mechanism: Token|mechanism string
            entity_data: Entity definition data
            
        Returns:
            Flow variable name
        """
        token = token_mechanism.split('|')[0]
        
        flow_mappings = {
            'mass': 'mass_flow_rate',
            'energy': 'heat_flow_rate', 
            'charge': 'current',
            'momentum': 'momentum_flow_rate'
        }
        
        return flow_mappings.get(token, f'{token}_flow_rate')
    
    def _extract_transport_equations(self) -> Dict[str, List[str]]:
        """
        Extract available transport equations from ontology
        
        Returns:
            Dictionary mapping tokens to available transport mechanisms
        """
        transport_equations = {}
        
        # Extract from ontology structure
        ontology_tree = self.ontology.get('ontology_tree', {})
        
        for domain_name, domain_data in ontology_tree.items():
            structure = domain_data.get('structure', {})
            arc_structure = structure.get('arc', {})
            
            for token, token_data in arc_structure.items():
                if token not in transport_equations:
                    transport_equations[token] = []
                
                for mechanism in token_data.keys():
                    if mechanism not in transport_equations[token]:
                        transport_equations[token].append(mechanism)
        
        return transport_equations
    
    def generate_dynamic_mappings(self) -> Dict[str, Dict[str, str]]:
        """
        Generate complete dynamic mappings
        
        Returns:
            Dictionary of all physical domain mappings
        """
        return self.effort_variable_mappings
    
    def add_new_transport_type(self, token: str, mechanism: str, effort_variable: str, 
                             flow_variable: Optional[str] = None) -> None:
        """
        Dynamically add a new transport type
        
        Args:
            token: Token type (mass, energy, etc.)
            mechanism: Transport mechanism (convection, diffusion, etc.)
            effort_variable: Driving effort variable
            flow_variable: Resulting flow variable (optional)
        """
        key = f"{token}|{mechanism}"
        
        if flow_variable is None:
            flow_variable = f"{token}_flow_rate"
        
        self.effort_variable_mappings[key] = {
            "effort_variable": effort_variable,
            "token": token,
            "transport_equation": mechanism,
            "flow_variable": flow_variable
        }
    
    def update_from_entity_changes(self, updated_entities: Dict[str, Any]) -> None:
        """
        Update mappings when entities change
        
        Args:
            updated_entities: Updated entity definitions
        """
        self.entities = updated_entities
        self.effort_variable_mappings = self._extract_effort_variable_mappings()


class DynamicArcOptionsGenerator:
    """
    Generates enhanced arc options dynamically from ontology and entities
    """
    
    def __init__(self, ontology_data: Dict[str, Any], entities_data: Dict[str, Any]):
        self.mapper = DynamicPhysicalDomainMapper(ontology_data, entities_data)
        self.ontology = ontology_data
        self.entities = entities_data
    
    def generate_enhanced_arc_options(self) -> Dict[str, Dict[str, Any]]:
        """
        Generate complete enhanced arc options
        
        Returns:
            Enhanced arc options with physical domain information
        """
        # Start with basic arc options generation (similar to existing system)
        basic_arc_options = self._generate_basic_arc_options()
        
        # Enhance with dynamic physical domain information
        enhanced_options = {}
        
        for arc_name, arc_data in basic_arc_options.items():
            enhanced_options[arc_name] = arc_data.copy()
            
            # Add dynamic physical domain info
            token_mechanism = self.mapper._extract_token_mechanism(arc_name)
            if token_mechanism and token_mechanism in self.mapper.effort_variable_mappings:
                enhanced_options[arc_name]["physical_domain"] = self.mapper.effort_variable_mappings[token_mechanism]
            else:
                enhanced_options[arc_name]["physical_domain"] = None
        
        return enhanced_options
    
    def _generate_basic_arc_options(self) -> Dict[str, Dict[str, Any]]:
        """
        Generate basic arc options (sources/sinks) - similar to existing system
        
        Returns:
            Basic arc options dictionary
        """
        arc_options = {}
        
        # Separate entities by type
        arc_entities = []
        node_entities = []
        
        for entity_name, entity_data in self.entities.items():
            if self.mapper._is_arc_entity(entity_name, entity_data):
                arc_entities.append(entity_name)
            elif self._is_node_entity(entity_name, entity_data):
                node_entities.append(entity_name)
        
        # Generate arc options for each arc entity
        for arc_entity_name in arc_entities:
            arc_options[arc_entity_name] = {
                "sources": [],
                "sinks": []
            }
            
            # Extract token from arc entity name
            arc_token = self.mapper._extract_token_mechanism(arc_entity_name)
            if arc_token:
                arc_token = arc_token.split('|')[0]  # Get just the token part
            else:
                continue  # Skip if no token found
            
            # Find compatible nodes based on token compatibility
            for node_entity_name in node_entities:
                node_entity_data = self.entities[node_entity_name]
                node_tokens = self._extract_entity_tokens_from_name(node_entity_name)
                
                # Check token compatibility
                if self._tokens_compatible([arc_token], node_tokens):
                    arc_options[arc_entity_name]["sources"].append(node_entity_name)
                    arc_options[arc_entity_name]["sinks"].append(node_entity_name)
        
        return arc_options
    
    def _is_node_entity(self, entity_name: str, entity_data: Dict[str, Any]) -> bool:
        """Check if entity is a node entity"""
        if ".node." in entity_name:
            return True
        
        if isinstance(entity_data, dict):
            if "entity_type" in entity_data and entity_data["entity_type"] == "node":
                return True
        
        return False
    
    def _extract_entity_tokens_from_name(self, entity_name: str) -> List[str]:
        """Extract tokens from entity name (not entity data)"""
        if ".node." in entity_name and "|" in entity_name:
            parts = entity_name.split('.')
            if len(parts) >= 3:
                token_part = parts[2]
                if '|' in token_part:
                    return [token_part.split('|')[0]]
        return []
    
    def _extract_entity_tokens(self, entity_data: Dict[str, Any]) -> List[str]:
        """Extract tokens from entity data"""
        # Extract from entity name if available
        if isinstance(entity_data, dict):
            entity_name = entity_data.get('name', '')
            # If entity_name is the full entity ID, extract token from it
            if '.' in entity_name and '|' in entity_name:
                parts = entity_name.split('.')
                if len(parts) >= 2:
                    token_part = parts[2]
                    if '|' in token_part:
                        return [token_part.split('|')[0]]
            
            # Try to infer token from variables
            variables = entity_data.get('variables', {})
            for var_name, var_data in variables.items():
                if isinstance(var_data, dict):
                    var_type = var_data.get('type', '').lower()
                    if var_type == 'effort':
                        # Infer token from effort variable name
                        if 'pressure' in var_name.lower():
                            return ['mass']
                        elif 'temperature' in var_name.lower():
                            return ['energy']
                        elif 'voltage' in var_name.lower():
                            return ['charge']
                        elif 'velocity' in var_name.lower() or 'stress' in var_name.lower():
                            return ['momentum']
        
        return []
    
    def _tokens_compatible(self, arc_tokens: List[str], node_tokens: List[str]) -> bool:
        """Check if arc and node tokens are compatible"""
        # Basic compatibility check - would need enhancement
        return bool(set(arc_tokens) & set(node_tokens))


if __name__ == "__main__":
    # Example usage
    print("Dynamic arc options generator initialized")
    print("This system can adapt to any ontology structure dynamically")
