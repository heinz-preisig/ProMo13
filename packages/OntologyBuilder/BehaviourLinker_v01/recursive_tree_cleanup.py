def recursive_tree_cleanup(forest_structure, var_to_remove):
    """
    Simple recursive cleanup that removes variables and dependent equations from tree.
    
    Args:
        forest_structure: list of tree dictionaries
        var_to_remove: variable to remove
        
    Returns:
        dict: {
            'cleaned_forest': list,
            'removed_equations': set,
            'removed_variables': set
        }
    """
    print(f"Starting recursive tree cleanup for variable: {var_to_remove}")
    
    removed_equations = set()
    removed_variables = set()
    
    # Work with a copy
    current_forest = []
    for tree in forest_structure:
        current_forest.append(tree.copy())
    
    # Recursive cleanup loop
    changed = True
    while changed:
        changed = False
        print(f"Cleanup iteration, variables to remove: {removed_variables}")
        print(f"Cleanup iteration, equations to remove: {removed_equations}")
        
        # Step 1: Remove target variables from all trees
        for tree in current_forest:
            if var_to_remove in tree:
                del tree[var_to_remove]
                print(f"Removed {var_to_remove} from tree")
        
        # Step 2: Find equations that should be removed
        equations_to_remove = set()
        for tree in current_forest:
            for key, values in list(tree.items()):
                if key.startswith('E_') and values:
                    # Check if all variables in this equation are either:
                    # 1. Already removed, or
                    # 2. The current target variable, or
                    # 3. Only used by this equation
                    all_vars_removable = True
                    for var in values:
                        if var not in removed_variables and var != var_to_remove:
                            # Check if this variable is used by other equations
                            used_by_other_eqs = False
                            for other_tree in current_forest:
                                if var in other_tree and other_tree[var]:
                                    for other_eq in other_tree[var]:
                                        if other_eq != key and other_eq not in removed_equations:
                                            used_by_other_eqs = True
                                            break
                                if used_by_other_eqs:
                                    break
                            
                            if not used_by_other_eqs:
                                # This variable is only used by this equation
                                all_vars_removable = False
                                print(f"Variable {var} is only used by equation {key}")
                                break
                    
                    if all_vars_removable:
                        equations_to_remove.add(key)
                        print(f"Equation {key} should be removed (all variables removable)")
        
        # Step 3: Remove equations and add their variables to removal list
        for eq_id in equations_to_remove:
            if eq_id not in removed_equations:
                removed_equations.add(eq_id)
                print(f"Removing equation {eq_id}")
                
                # Find variables defined by this equation
                for tree in current_forest:
                    if eq_id in tree:
                        vars_defined = tree[eq_id]
                        print(f"Variables defined by {eq_id}: {vars_defined}")
                        
                        # Add all variables to removal list (except those used by other equations)
                        for var in vars_defined:
                            if var not in removed_variables:
                                # Check if used by other equations
                                used_by_other = False
                                for other_tree in current_forest:
                                    if var in other_tree and other_tree[var]:
                                        for other_eq in other_tree[var]:
                                            if other_eq != eq_id and other_eq not in removed_equations:
                                                used_by_other = True
                                                break
                                    if used_by_other:
                                        break
                                
                                if not used_by_other:
                                    removed_variables.add(var)
                                    print(f"Added variable {var} to removal list (only used by {eq_id})")
                        
                        # Remove equation from tree
                        del tree[eq_id]
                        break
        
        # Step 4: Add target variable to removed list
        if var_to_remove not in removed_variables:
            removed_variables.add(var_to_remove)
            changed = True
        
        # Clean up empty trees
        current_forest = [tree for tree in current_forest if tree]
        
        print(f"Iteration completed. Removed equations: {removed_equations}, Removed variables: {removed_variables}")
    
    print(f"Recursive cleanup completed:")
    print(f"  Removed equations: {removed_equations}")
    print(f"  Removed variables: {removed_variables}")
    print(f"  Cleaned forest: {current_forest}")
    
    return {
        'cleaned_forest': current_forest,
        'removed_equations': removed_equations,
        'removed_variables': removed_variables
    }
