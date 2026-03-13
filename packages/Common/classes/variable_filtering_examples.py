"""
Example usage of the integrated variable filtering in exchange_board.py

This demonstrates how the unified filtering system can be used by both
Entity classes and Behaviour Linker components.
"""

# Example for Entity class usage
def example_entity_filtering(ontology_board, entity):
    """Example of how Entity classes can use the new filtering methods."""
    
    # Get entity's equation-defined variables
    equation_defined_vars = entity.get_equation_defined_vars()
    
    # Use exchange board for transport filtering (replaces internal logic)
    filtered_output_vars = ontology_board.get_output_variables_filtered(
        equation_defined_vars, 
        exclude_transport=True
    )
    
    # Alternative: Filter by component type
    node_variables = ontology_board.filter_variables_by_component(
        entity.variables, 
        'node'
    )
    
    # Filter by specific networks
    macroscopic_vars = ontology_board.filter_variables_by_network(
        entity.variables,
        ['macroscopic']
    )
    
    return filtered_output_vars, node_variables, macroscopic_vars


# Example for Behaviour Linker usage
def example_behaviour_linker_filtering(ontology_board, entity_type_info):
    """Example of how Behaviour Linker can use the new filtering methods."""
    
    # Get filtered variables for different modes (replaces internal logic)
    state_vars = ontology_board.filter_variables_for_behaviour_linker(
        entity_type_info, 
        'state'
    )
    
    transport_vars = ontology_board.filter_variables_for_behaviour_linker(
        entity_type_info, 
        'transport'
    )
    
    intensity_vars = ontology_board.filter_variables_for_behaviour_linker(
        entity_type_info, 
        'intensity'
    )
    
    all_vars = ontology_board.filter_variables_for_behaviour_linker(
        entity_type_info, 
        'all'
    )
    
    return state_vars, transport_vars, intensity_vars, all_vars


# Example for interface/intraface usage
def example_interface_filtering(ontology_board):
    """Example of interface-specific variable filtering."""
    
    # Get variables for specific interface
    interface_vars = ontology_board.get_variables_for_interface(
        'macroscopic|info_processing'
    )
    
    # Get variables for specific intraface
    intraface_vars = ontology_board.get_variables_for_intraface(
        'some_intraface_network'
    )
    
    return interface_vars, intraface_vars


# Example of direct filtering methods
def example_direct_filtering(ontology_board):
    """Example of using the direct filtering methods."""
    
    # Filter by type directly
    state_vars = ontology_board.filter_variables_by_type(
        ontology_board.variables,
        ['state', 'secondaryState']
    )
    
    # Filter out transport variables
    non_transport_vars = ontology_board.filter_transport_variables(
        ontology_board.variables
    )
    
    # Filter for only transport variables
    transport_only = ontology_board.filter_only_transport(
        ontology_board.variables
    )
    
    return state_vars, non_transport_vars, transport_only


"""
Migration Guide:

1. Entity Classes:
   - Replace: entity.get_equation_defined_vars(all_variables)
   - With: ontology_board.get_output_variables_filtered(entity.get_equation_defined_vars())

2. Behaviour Linker:
   - Replace: VariableClassificationRules.filter_variables_by_type()
   - With: ontology_board.filter_variables_for_behaviour_linker()

3. General Filtering:
   - Replace: Custom filtering logic
   - With: ontology_board.filter_variables_by_type(), filter_variables_by_network(), etc.

Benefits:
- Single source of truth for variable filtering
- Leverages existing ontology infrastructure
- Consistent behavior across all components
- Easy to extend with new filtering criteria
- Better performance (uses cached variable type data)
"""
