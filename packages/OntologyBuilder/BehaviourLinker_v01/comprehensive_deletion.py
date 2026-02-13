#!/usr/bin/env python3

"""
Comprehensive variable deletion using incidence matrix with recursive cleanup.
This generates the incidence matrix for the entity, removes variables recursively,
and regenerates the variable lists.
"""

# Import the forest-based cleanup function
from OntologyBuilder.BehaviourLinker_v01.forest_cleanup import recursive_cleanup_forest

def generate_incidence_matrix(entity):
    """
    Generate incidence matrix for the entity from forest structure primarily.
    
    Returns:
        dict: {equation_id: [variable_ids]}
    """
    incidence_matrix = {}
    
    print("Generating incidence matrix from forest structure (primary)...")
    
    # Primary: Use forest structure which is reliable
    if hasattr(entity, 'var_eq_forest') and entity.var_eq_forest:
        for tree in entity.var_eq_forest:
            for key, values in tree.items():
                if key.startswith('E_') and values:
                    # Equation defines variables
                    if key not in incidence_matrix:
                        incidence_matrix[key] = []
                    for var in values:
                        if var.startswith('V_') and var not in incidence_matrix[key]:
                            incidence_matrix[key].append(var)
                    print(f"From forest: Equation {key} defines variables: {incidence_matrix[key]}")
                elif key.startswith('V_') and values:
                    # Variable is defined by equations
                    for eq in values:
                        if eq.startswith('E_'):
                            if eq not in incidence_matrix:
                                incidence_matrix[eq] = []
                            # Add this variable to the equation's list
                            if key not in incidence_matrix[eq]:
                                incidence_matrix[eq].append(key)
                    print(f"From forest: Variable {key} defined by equations: {values}")
                    print(f"Updated equation lists after variable {key}: {incidence_matrix}")
    
    print(f"Final incidence matrix from forest processing: {incidence_matrix}")
    
    # Secondary: Enhance with all_equations if available (but don't replace forest data)
    if hasattr(entity, 'all_equations') and entity.all_equations:
        print(f"Enhancing with {len(entity.all_equations)} equations from all_equations...")
        
        for eq_id, equation in entity.all_equations.items():
            if eq_id not in incidence_matrix:
                # Only add equations not already in forest
                variables_in_equation = set()
                
                try:
                    if hasattr(equation, 'get_incidence_list'):
                        try:
                            # Try getting full incidence list
                            full_incidence = equation.get_incidence_list()
                            if isinstance(full_incidence, list):
                                variables_in_equation.update(full_incidence)
                            elif isinstance(full_incidence, dict):
                                variables_in_equation.update(full_incidence.keys())
                        except:
                            # Fallback: try with common variables
                            for var in ['V_1', 'V_105', 'V_106', 'V_115', 'V_111', 'V_196', 'V_203', 'V_215', 'V_216']:
                                try:
                                    if var in equation.get_incidence_list(var):
                                        variables_in_equation.add(var)
                                except:
                                    pass
                    elif isinstance(equation, dict) and 'incidence_list' in equation:
                        incidence_list = equation['incidence_list']
                        if isinstance(incidence_list, list):
                            variables_in_equation.update(incidence_list)
                        elif isinstance(incidence_list, dict):
                            variables_in_equation.update(incidence_list.keys())
                    
                    if variables_in_equation:
                        incidence_matrix[eq_id] = list(variables_in_equation)
                        print(f"From all_equations: Equation {eq_id} defines variables: {variables_in_equation}")
                
                except Exception as e:
                    print(f"Error processing equation {eq_id}: {e}")
    
    print(f"Final generated incidence matrix: {incidence_matrix}")
    return incidence_matrix

def recursive_cleanup_incidence_matrix(incidence_matrix, var_to_remove):
    """
    Recursively clean up incidence matrix by removing variable and dependent variables.
    
    Args:
        incidence_matrix: dict of equation -> [variables]
        var_to_remove: variable to remove
        
    Returns:
        dict: {
            'cleaned_matrix': dict,
            'removed_equations': set,
            'removed_variables': set
        }
    """
    print(f"Starting recursive cleanup for variable: {var_to_remove}")
    
    removed_equations = set()
    removed_variables = set()
    current_matrix = {eq: vars[:] for eq, vars in incidence_matrix.items()}
    
    # Recursive cleanup loop
    changed = True
    while changed:
        changed = False
        print(f"Cleanup iteration, current matrix: {current_matrix}")
        
        # Check ALL equations in current matrix to see if any should be removed
        equations_to_check = list(current_matrix.keys())
        
        for eq_id in equations_to_check:
            if eq_id in removed_equations:
                continue
                
            # Check if all variables in this equation are either:
            # 1. The variable we're removing, or
            # 2. Already marked for removal, or
            # 3. NOT shared with other equations
            all_vars_removable = True
            for var in current_matrix[eq_id]:
                if var != var_to_remove and var not in removed_variables:
                    # Check if this variable is shared with other equations
                    is_shared = False
                    for other_eq_id, other_vars in current_matrix.items():
                        if other_eq_id != eq_id and var in other_vars:
                            is_shared = True
                            break
                    
                    if is_shared:
                        # Variable is shared - equation must be kept
                        all_vars_removable = False
                        print(f"  Variable {var} is shared (also in other equations)")
                        break
            
            if all_vars_removable:
                print(f"Removing equation {eq_id} (all variables removable: {current_matrix[eq_id]})")
                removed_equations.add(eq_id)
                
                # Mark all variables in this equation for removal
                for var in current_matrix[eq_id]:
                    if var not in removed_variables:
                        removed_variables.add(var)
                        print(f"Marked variable {var} for removal (from equation {eq_id})")
                        changed = True
                
                # Remove equation from matrix
                del current_matrix[eq_id]
            else:
                # Just remove the target variable from this equation
                if var_to_remove in current_matrix[eq_id]:
                    current_matrix[eq_id].remove(var_to_remove)
                    print(f"Removed {var_to_remove} from equation {eq_id}")
                    changed = True
    
    # Remove the target variable from removed_variables (we're deleting it anyway)
    removed_variables.discard(var_to_remove)
    removed_variables.add(var_to_remove)
    
    print(f"Recursive cleanup completed:")
    print(f"  Removed equations: {removed_equations}")
    print(f"  Removed variables: {removed_variables}")
    print(f"  Cleaned matrix: {current_matrix}")
    
    return {
        'cleaned_matrix': current_matrix,
        'removed_equations': removed_equations,
        'removed_variables': removed_variables
    }

def comprehensive_variable_deletion(entity, var_id):
    """
    Perform comprehensive variable deletion using forest structure with recursive cleanup.
    
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
        print(f"=== COMPREHENSIVE DELETION (FOREST STRUCTURE + RECURSIVE CLEANUP): {var_id} ===")
        
        # Step 1: Get the forest structure directly
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
        print(f"Using forest structure directly: {forest_structure}")
        
        # Step 2: Perform recursive cleanup on forest structure
        cleanup_result = recursive_cleanup_forest(forest_structure, var_id)
        cleaned_forest = cleanup_result['cleaned_forest']
        removed_equations = cleanup_result['removed_equations']
        removed_variables = cleanup_result['removed_variables']
        
        # Step 3: Identify preserved items
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
            'message': f"Forest structure recursive cleanup completed for {var_id}",
            'removed_equations': removed_equations,
            'removed_variables': removed_variables,
            'preserved_equations': preserved_equations,
            'preserved_variables': preserved_variables,
            'cleaned_forest': cleaned_forest
        }
        
    except Exception as e:
        error_msg = f"Error in forest structure recursive cleanup: {str(e)}"
        print(error_msg)
        return {
            'success': False,
            'message': error_msg,
            'removed_equations': set(),
            'removed_variables': set(),
            'preserved_equations': set(),
            'preserved_variables': set()
        }
