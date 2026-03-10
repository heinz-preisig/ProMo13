#!/usr/local/bin/python3
# encoding: utf-8

"""
Enhanced arc options saver with physical domain information
Includes effort variables, tokens, and transport equations for physical domain arcs
"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path

# Standard effort variable mappings for physical transport equations
PHYSICAL_DOMAIN_MAPPINGS = {
    # Mass transport
    "mass|convection": {
        "effort_variable": "pressure",
        "token": "mass",
        "transport_equation": "convection",
        "flow_variable": "mass_flow_rate"
    },
    "mass|diffusion": {
        "effort_variable": "chemical_potential",
        "token": "mass", 
        "transport_equation": "diffusion",
        "flow_variable": "mass_flow_rate"
    },
    
    # Energy transport
    "energy|conduction": {
        "effort_variable": "temperature",
        "token": "energy",
        "transport_equation": "conduction", 
        "flow_variable": "heat_flow_rate"
    },
    "energy|convection": {
        "effort_variable": "temperature",
        "token": "energy",
        "transport_equation": "convection",
        "flow_variable": "heat_flow_rate"
    },
    
    # Charge transport
    "charge|conduction": {
        "effort_variable": "voltage",
        "token": "charge",
        "transport_equation": "conduction",
        "flow_variable": "current"
    },
    
    # Momentum transport
    "momentum|convection": {
        "effort_variable": "velocity",
        "token": "momentum",
        "transport_equation": "convection",
        "flow_variable": "momentum_flow_rate"
    },
    "momentum|diffusion": {
        "effort_variable": "stress",
        "token": "momentum",
        "transport_equation": "viscous_diffusion",
        "flow_variable": "momentum_flow_rate"
    }
}


def extract_physical_domain_info(arc_entity_name: str, entity_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """
    Extract physical domain information for an arc entity
    
    Args:
        arc_entity_name: Name of the arc entity (e.g., "macroscopic.arc.mass|convection|lumped.convectiveMassFlow")
        entity_data: Dictionary containing entity information
        
    Returns:
        Dictionary with physical domain info or None if not applicable
    """
    # Parse the arc entity name to extract token and mechanism
    # Format: domain.arc.token|mechanism|type.entityName
    try:
        parts = arc_entity_name.split('.')
        if len(parts) < 4:
            return None
            
        # Extract token and mechanism
        token_mechanism_part = parts[2]  # e.g., "mass|convection"
        token_mechanism = token_mechanism_part.split('|')
        
        if len(token_mechanism) >= 2:
            token = token_mechanism[0]
            mechanism = token_mechanism[1]
            key = f"{token}|{mechanism}"
            
            if key in PHYSICAL_DOMAIN_MAPPINGS:
                return PHYSICAL_DOMAIN_MAPPINGS[key].copy()
                
    except (IndexError, AttributeError):
        pass
        
    return None


def enhance_arc_options_with_physical_domain(arc_options: Dict[str, Dict[str, Any]], 
                                          all_entities: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Enhance arc options with physical domain information
    
    Args:
        arc_options: Original arc options dictionary
        all_entities: Dictionary of all entities
        
    Returns:
        Enhanced arc options with physical domain information
    """
    enhanced_arc_options = {}
    
    for arc_name, arc_data in arc_options.items():
        enhanced_arc_options[arc_name] = arc_data.copy()
        
        # Add physical domain info for physical arcs
        physical_info = extract_physical_domain_info(arc_name, all_entities.get(arc_name, {}))
        enhanced_arc_options[arc_name]["physical_domain"] = physical_info
        
    return enhanced_arc_options


def save_enhanced_arc_options_to_file(ontology_name: str, 
                                    arc_options: Dict[str, Dict[str, Any]], 
                                    all_entities: Optional[Dict[str, Any]] = None,
                                    output_path: Optional[str] = None) -> None:
    """
    Save enhanced arc options to file with physical domain information
    
    Args:
        ontology_name: Name of the ontology
        arc_options: Arc options dictionary
        all_entities: Optional dictionary of all entities for extracting physical domain info
        output_path: Optional custom output path
    """
    # Enhance with physical domain information if entities are provided
    if all_entities is not None:
        arc_options = enhance_arc_options_with_physical_domain(arc_options, all_entities)
    
    # Determine output path
    if output_path is None:
        output_path = f"enhanced_arc_options_{ontology_name}.json"
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(arc_options, file, indent=4)
    
    print(f"Enhanced arc options saved to: {output_path}")


def load_enhanced_arc_options_from_file(file_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Load enhanced arc options from file
    
    Args:
        file_path: Path to the enhanced arc options file
        
    Returns:
        Dictionary containing enhanced arc options
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def validate_physical_domain_consistency(arc_options: Dict[str, Dict[str, Any]]) -> List[str]:
    """
    Validate physical domain consistency in arc options
    
    Args:
        arc_options: Enhanced arc options dictionary
        
    Returns:
        List of validation warnings/errors
    """
    warnings = []
    
    for arc_name, arc_data in arc_options.items():
        physical_domain = arc_data.get("physical_domain")
        
        if physical_domain is not None:
            # Check required fields
            required_fields = ["effort_variable", "token", "transport_equation", "flow_variable"]
            for field in required_fields:
                if field not in physical_domain:
                    warnings.append(f"Missing '{field}' in physical_domain for {arc_name}")
            
            # Check that sources and sinks are compatible with token
            token = physical_domain.get("token")
            if token:
                sources = arc_data.get("sources", [])
                sinks = arc_data.get("sinks", [])
                
                for source in sources:
                    if token not in source:
                        warnings.append(f"Source {source} may not be compatible with token {token} for {arc_name}")
                        
                for sink in sinks:
                    if token not in sink:
                        warnings.append(f"Sink {sink} may not be compatible with token {token} for {arc_name}")
    
    return warnings


if __name__ == "__main__":
    # Example usage
    example_arc_options = {
        "macroscopic.arc.mass|convection|lumped.convectiveMassFlow": {
            "sources": ["macroscopic.node.mass|dynamic|lumped.dynamicMass"],
            "sinks": ["macroscopic.node.mass|constant|infinity.massSource"]
        }
    }
    
    # Save enhanced version
    save_enhanced_arc_options_to_file("example", example_arc_options)
    
    # Validate
    enhanced = load_enhanced_arc_options_from_file("enhanced_arc_options_example.json")
    warnings = validate_physical_domain_consistency(enhanced)
    
    if warnings:
        print("Validation warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("Validation passed!")
