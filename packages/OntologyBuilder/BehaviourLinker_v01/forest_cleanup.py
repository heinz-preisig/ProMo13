def recursive_cleanup_forest(forest_structure, var_to_remove):
    """
    Recursively clean up forest structure using stack-based approach.
    
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
    print(f"Starting recursive forest cleanup for variable: {var_to_remove}")
    
    removed_equations = set()
    removed_variables = set()
    
    # Work with a copy of the forest
    current_forest = []
    for tree in forest_structure:
        current_forest.append(tree.copy())
    
    # Stack-based recursive cleanup
    var_stack = [var_to_remove]
    
    while var_stack:
        current_var = var_stack.pop()
        print(f"Processing variable from stack: {current_var}")
        print(f"Current stack: {var_stack}")
        
        if current_var in removed_variables:
            print(f"Variable {current_var} already processed")
            continue
        
        # Find equations that define this variable in the forest
        equations_with_var = []
        for tree in current_forest:
            if current_var in tree and tree[current_var]:
                equations_with_var.extend(tree[current_var])
        
        # Remove duplicates
        equations_with_var = list(set(equations_with_var))
        print(f"Equations that define {current_var}: {equations_with_var}")
        
        # For each equation, remove the variable and check if equation should be removed
        for eq_id in equations_with_var:
            if eq_id in removed_equations:
                continue
            
            print(f"Processing equation {eq_id}")
            
            # Find variables defined by this equation
            vars_defined_by_eq = []
            for tree in current_forest:
                if eq_id in tree:
                    vars_defined_by_eq = tree[eq_id]
                    break
            
            print(f"Variables defined by {eq_id}: {vars_defined_by_eq}")
            
            # Remove current_var from equation's variable list
            if current_var in vars_defined_by_eq:
                vars_defined_by_eq.remove(current_var)
                print(f"Removed {current_var} from {eq_id}")
            
            if not vars_defined_by_eq:
                # Equation defines no variables - remove it
                print(f"Removing equation {eq_id} (defines no variables)")
                removed_equations.add(eq_id)
                
                # Remove equation from all trees
                for tree in current_forest:
                    if eq_id in tree:
                        del tree[eq_id]
            else:
                # Check if remaining variables are shared with other equations
                shared_vars = set()
                unique_vars = set()
                
                for var in vars_defined_by_eq:
                    is_shared = False
                    for tree in current_forest:
                        if var in tree and tree[var]:
                            for other_eq in tree[var]:
                                if other_eq != eq_id and other_eq not in removed_equations:
                                    is_shared = True
                                    shared_vars.add(var)
                                    break
                        if is_shared:
                            break
                    
                    if not is_shared:
                        unique_vars.add(var)
                
                print(f"Shared variables in {eq_id}: {shared_vars}")
                print(f"Unique variables in {eq_id}: {unique_vars}")
                
                if not unique_vars:
                    # All variables are shared - keep equation
                    print(f"Keeping equation {eq_id} (all variables shared)")
                else:
                    # Equation has unique variables - check if it should be removed
                    # For now, keep equations with any shared variables
                    print(f"Keeping equation {eq_id} (has shared variables)")
        
        # Mark current variable as removed
        removed_variables.add(current_var)
        print(f"Marked variable {current_var} as removed")
        
        # Remove variable from all trees
        for tree in current_forest:
            if current_var in tree:
                del tree[current_var]
        
        # Check for equations that should now be removed (only define removed/shared variables)
        equations_to_remove = []
        for tree in current_forest:
            for eq_id, vars_list in list(tree.items()):
                if eq_id.startswith('E_') and eq_id not in removed_equations:
                    # Check if all variables defined by this equation are removed or shared
                    should_remove = True
                    for var in vars_list:
                        if var not in removed_variables:
                            # Check if this variable is shared with other equations
                            is_shared = False
                            for other_tree in current_forest:
                                if var in other_tree and other_tree[var]:
                                    for other_eq in other_tree[var]:
                                        if other_eq != eq_id and other_eq not in removed_equations:
                                            is_shared = True
                                            break
                                if is_shared:
                                    break
                            
                            if not is_shared:
                                # Variable is not removed and not shared
                                should_remove = False
                                break
                    
                    if should_remove:
                        equations_to_remove.append(eq_id)
        
        # Remove identified equations and add their variables to stack
        for eq_id in equations_to_remove:
            print(f"Queueing equation {eq_id} for removal")
            removed_equations.add(eq_id)
            
            # Find variables defined by this equation
            for tree in current_forest:
                if eq_id in tree:
                    vars_to_add = tree[eq_id]
                    print(f"Adding variables to stack from {eq_id}: {vars_to_add}")
                    
                    for var in vars_to_add:
                        if var not in removed_variables:
                            var_stack.append(var)
                    
                    del tree[eq_id]
                    break
    
    # Clean up empty trees
    cleaned_forest = [tree for tree in current_forest if tree]
    
    print(f"Recursive forest cleanup completed:")
    print(f"  Removed equations: {removed_equations}")
    print(f"  Removed variables: {removed_variables}")
    print(f"  Cleaned forest: {cleaned_forest}")
    
    return {
        'cleaned_forest': cleaned_forest,
        'removed_equations': removed_equations,
        'removed_variables': removed_variables
    }
