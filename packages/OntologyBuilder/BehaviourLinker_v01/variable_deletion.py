#!/usr/bin/env python3

"""
Enhanced variable deletion with dependency analysis for entity editor.
This module provides intelligent variable deletion that:
1. Analyzes variable dependencies in the equation forest
2. Removes dependent equations and orphaned variables
3. Maintains entity structure integrity
"""

def handle_variable_deletion_with_dependencies(entity, var_id):
    """
    Enhanced variable deletion with comprehensive dependency analysis.
    
    This function now delegates to the Entity's own delete_variable_with_dependencies method,
    which handles the entire process internally including dependency analysis, forest cleanup,
    and entity rebuilding.
    
    Args:
        entity: The Entity object to modify
        var_id: The variable ID to delete
        
    Returns:
        tuple: (success, message, dependent_equations, orphaned_variables)
    """
    try:
        print(f"=== ENHANCED VARIABLE DELETION: {var_id} ===")
        
        # Delegate to Entity's own comprehensive deletion method
        if hasattr(entity, 'delete_variable_with_dependencies'):
            success, message, dependent_equations, orphaned_variables = entity.delete_variable_with_dependencies(var_id)
            return success, message, dependent_equations, orphaned_variables
        else:
            return False, "Entity does not support variable deletion", set(), set()
            
    except Exception as e:
        print(f"Error in handle_variable_deletion_with_dependencies: {e}")
        return False, f"Error deleting variable: {str(e)}", set(), set()
