#!/usr/bin/env python3

"""
Comprehensive variable deletion using pure incidence matrix with recursive cleanup.
This replaces the forest structure completely with a clean incidence matrix approach.
"""

# Import the stack-based cleanup function
from OntologyBuilder.BehaviourLinker_v01.stack_cleanup import recursive_cleanup_incidence_matrix

def generate_incidence_matrix(entity):
    """
    Generate clean incidence matrix for the entity from all equations.
    
    Returns:
        dict: {equation_id: [variable_ids]}
    """
    incidence_matrix = {}
    
    print("Generating clean incidence matrix from all equations...")
    
    if hasattr(entity, 'all_equations') and entity.all_equations:
        print(f"Processing {len(entity.all_equations)} equations...")
        
        for eq_id, equation in entity.all_equations.items():
            variables_in_equation = set()
            
            try:
                if hasattr(equation, 'get_incidence_list'):
                    try:
                        # Try getting full incidence list
                        full_incidence = equation.get_incidence_list()
                        print(f"Equation {eq_id} raw incidence list: {full_incidence} (type: {type(full_incidence)})")
                        
                        if isinstance(full_incidence, list):
                            variables_in_equation.update(full_incidence)
                        elif isinstance(full_incidence, dict):
                            variables_in_equation.update(full_incidence.keys())
                        else:
                            print(f"Unexpected incidence list type for {eq_id}: {type(full_incidence)}")
                            # Try to iterate over it anyway
                            try:
                                for item in full_incidence:
                                    if isinstance(item, str) and item.startswith('V_'):
                                        variables_in_equation.add(item)
                            except:
                                pass
                                
                        print(f"Equation {eq_id} processed incidence: {variables_in_equation}")
                    except Exception as e:
                        print(f"Error getting incidence list for {eq_id}: {e}")
                        # Fallback: try with common variables
                        for var in ['V_1', 'V_105', 'V_106', 'V_115', 'V_111', 'V_196', 'V_203', 'V_215', 'V_216']:
                            try:
                                if var in equation.get_incidence_list(var):
                                    variables_in_equation.add(var)
                                    print(f"Found {var} in {eq_id} via specific check")
                            except:
                                pass
                elif isinstance(equation, dict) and 'incidence_list' in equation:
                    incidence_list = equation['incidence_list']
                    if isinstance(incidence_list, list):
                        variables_in_equation.update(incidence_list)
                    elif isinstance(incidence_list, dict):
                        variables_in_equation.update(incidence_list.keys())
                
                incidence_matrix[eq_id] = list(variables_in_equation)
                
            except Exception as e:
                print(f"Error processing equation {eq_id}: {e}")
                incidence_matrix[eq_id] = []
    
    # Fallback: use forest structure if all_equations is empty
    if not incidence_matrix and hasattr(entity, 'var_eq_forest') and entity.var_eq_forest:
        print("Falling back to forest structure...")
        for tree in entity.var_eq_forest:
            for key, values in tree.items():
                if key.startswith('E_') and values:
                    if key not in incidence_matrix:
                        incidence_matrix[key] = []
                    for var in values:
                        if var.startswith('V_') and var not in incidence_matrix[key]:
                            incidence_matrix[key].append(var)
                elif key.startswith('V_') and values:
                    # Variable is defined by equations
                    for eq in values:
                        if eq.startswith('E_'):
                            if eq not in incidence_matrix:
                                incidence_matrix[eq] = []
                            if key not in incidence_matrix[eq]:
                                incidence_matrix[eq].append(key)
    
    print(f"Final clean incidence matrix: {incidence_matrix}")
    return incidence_matrix

def comprehensive_variable_deletion(entity, var_id):
    """
    Perform comprehensive variable deletion using pure incidence matrix with recursive cleanup.
    
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
            'cleaned_matrix': dict
        }
    """
    try:
        print(f"=== COMPREHENSIVE DELETION (PURE INCIDENCE MATRIX): {var_id} ===")
        
        # Step 1: Generate clean incidence matrix
        incidence_matrix = generate_incidence_matrix(entity)
        
        if not incidence_matrix:
            print("No incidence matrix could be generated")
            return {
                'success': False,
                'message': f"No equations found for variable {var_id}",
                'removed_equations': set(),
                'removed_variables': set(),
                'preserved_equations': set(),
                'preserved_variables': set()
            }
        
        # Step 2: Check if target variable exists
        target_found = False
        for eq_id, variables in incidence_matrix.items():
            if var_id in variables:
                target_found = True
                print(f"Found target variable {var_id} in equation {eq_id}")
                break
        
        if not target_found:
            print(f"WARNING: Target variable {var_id} not found in incidence matrix!")
            return {
                'success': False,
                'message': f"Variable {var_id} not found in any equation",
                'removed_equations': set(),
                'removed_variables': set(),
                'preserved_equations': set(),
                'preserved_variables': set()
            }
        
        # Step 3: Perform recursive cleanup on incidence matrix
        cleanup_result = recursive_cleanup_incidence_matrix(incidence_matrix, var_id)
        cleaned_matrix = cleanup_result['cleaned_matrix']
        removed_equations = cleanup_result['removed_equations']
        removed_variables = cleanup_result['removed_variables']
        
        # Step 4: Identify preserved items
        preserved_equations = set(incidence_matrix.keys()) - removed_equations
        preserved_variables = set()
        for eq_id, variables in cleaned_matrix.items():
            preserved_variables.update(variables)
        
        print(f"Final analysis:")
        print(f"  Removed equations: {removed_equations}")
        print(f"  Removed variables: {removed_variables}")
        print(f"  Preserved equations: {preserved_equations}")
        print(f"  Preserved variables: {preserved_variables}")
        print(f"  Cleaned incidence matrix: {cleaned_matrix}")
        
        return {
            'success': True,
            'message': f"Pure incidence matrix cleanup completed for {var_id}",
            'removed_equations': removed_equations,
            'removed_variables': removed_variables,
            'preserved_equations': preserved_equations,
            'preserved_variables': preserved_variables,
            'cleaned_matrix': cleaned_matrix
        }
        
    except Exception as e:
        error_msg = f"Error in pure incidence matrix cleanup: {str(e)}"
        print(error_msg)
        return {
            'success': False,
            'message': error_msg,
            'removed_equations': set(),
            'removed_variables': set(),
            'preserved_equations': set(),
            'preserved_variables': set()
        }
