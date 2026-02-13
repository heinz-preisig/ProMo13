#!/usr/bin/env python3

"""
Simple comprehensive variable deletion using forest structure directly.
This avoids the complexity of incidence matrix conversion and works with what we know works.
"""

from OntologyBuilder.BehaviourLinker_v01.simple_forest_cleanup import simple_forest_cleanup

def simple_comprehensive_deletion(entity, var_id):
    """
    Perform comprehensive variable deletion using forest structure directly.
    
    Args:
        entity: The Entity object
        var_id: Variable ID to delete
        
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'removed_equations': set,
            'removed_variables': set,
            'preserved_equations': set,
            'preserved_variables': set,
            'cleaned_forest': list
        }
    """
    try:
        print(f"=== SIMPLE COMPREHENSIVE DELETION (FOREST DIRECT): {var_id} ===")
        
        # Step 1: Get the forest structure
        if not hasattr(entity, 'var_eq_forest') or not entity.var_eq_forest:
            print("No forest structure found")
            return {
                'success': False,
                'message': f"No forest structure found for variable {var_id}",
                'removed_equations': set(),
                'removed_variables': set(),
                'preserved_equations': set(),
                'preserved_variables': set()
            }
        
        forest_structure = entity.var_eq_forest
        print(f"Using forest structure: {forest_structure}")
        
        # Step 2: Check if target variable exists in forest
        target_found = False
        for tree in forest_structure:
            if var_id in tree:
                target_found = True
                print(f"Found target variable {var_id} in forest")
                break
        
        if not target_found:
            print(f"WARNING: Target variable {var_id} not found in forest structure!")
            return {
                'success': False,
                'message': f"Variable {var_id} not found in forest structure",
                'removed_equations': set(),
                'removed_variables': set(),
                'preserved_equations': set(),
                'preserved_variables': set()
            }
        
        # Step 3: Perform simple forest cleanup
        cleanup_result = simple_forest_cleanup(forest_structure, var_id)
        cleaned_forest = cleanup_result['cleaned_forest']
        removed_equations = cleanup_result['removed_equations']
        removed_variables = cleanup_result['removed_variables']
        
        # Step 4: Identify preserved items
        preserved_equations = set()
        preserved_variables = set()
        
        for tree in forest_structure:
            for key, values in tree.items():
                if key.startswith('E_') and key not in removed_equations:
                    preserved_equations.add(key)
                elif key.startswith('V_') and key not in removed_variables:
                    preserved_variables.add(key)
        
        print(f"Final analysis:")
        print(f"  Removed equations: {removed_equations}")
        print(f"  Removed variables: {removed_variables}")
        print(f"  Preserved equations: {preserved_equations}")
        print(f"  Preserved variables: {preserved_variables}")
        print(f"  Cleaned forest: {cleaned_forest}")
        
        return {
            'success': True,
            'message': f"Simple forest cleanup completed for {var_id}",
            'removed_equations': removed_equations,
            'removed_variables': removed_variables,
            'preserved_equations': preserved_equations,
            'preserved_variables': preserved_variables,
            'cleaned_forest': cleaned_forest
        }
        
    except Exception as e:
        error_msg = f"Error in simple forest cleanup: {str(e)}"
        print(error_msg)
        return {
            'success': False,
            'message': error_msg,
            'removed_equations': set(),
            'removed_variables': set(),
            'preserved_equations': set(),
            'preserved_variables': set()
        }
